import pandas as pd
import json
import warnings
from .core.parse_base import ParserBase
from .core.parse_daily import ParserDaily
from .core.parse_monthly import ParserMonthly


class PiyologParser:
    def __init__(self):
        pass

    def parse(self, filepath: str) -> dict:
        parser = ParserBase()
        is_valid, message = parser.validate_piyolog_file(filepath)
        if not is_valid:
            return {"status": "invalid", "message": message}

        daily_or_monthly = parser.check_daily_or_monthly(filepath)
        if daily_or_monthly not in ["daily", "monthly"]:
            return {"status": "invalid", "message": "unknown format"}

        with open(filepath) as f:
            lines = f.readlines()

        warnings_list = []

        try:
            if daily_or_monthly == "daily":
                parser = ParserDaily()

                # `warnings.catch_warnings()` で警告をキャッチ
                with warnings.catch_warnings(record=True) as caught_warnings:
                    warnings.simplefilter("always")  # すべての警告をキャッチ
                    data = parser.parse(lines)
                    if data["status"] == "invalid":
                        raise ValueError(data["message"])

                    # キャッチした警告をリストに追加
                    for w in caught_warnings:
                        warnings_list.append(str(w.message))

                return {"status": "valid", "daily_or_monthly": "daily", "data": data, "warnings": warnings_list}

            elif daily_or_monthly == "monthly":
                parser = ParserMonthly()
                splited_blocks = parser.split_daily_blocks(lines)
                if splited_blocks["status"] == "invalid":
                    return {"status": "invalid", "daily_or_monthly": "monthly", "message": splited_blocks["message"]}

                data = []
                parser = ParserDaily()
                daily_blocks = splited_blocks["daily_blocks"]

                for daily_block in daily_blocks:
                    try:
                        with warnings.catch_warnings(record=True) as caught_warnings:
                            warnings.simplefilter("always")
                            daily_data = parser.parse(daily_block)

                            for w in caught_warnings:
                                warnings_list.append(str(w.message))

                            data.append(daily_data)

                    except Exception as e:
                        return {"status": "invalid", "message": str(e)}

                return {"status": "valid", "daily_or_monthly": "monthly", "data": data, "warnings": warnings_list}

        except Exception as e:
            return {"status": "invalid", "message": str(e)}

    def get_timeline_df(self, parsed_data) -> pd.DataFrame:
        if parsed_data["status"] != "valid":
            raise ValueError(f"Cannot generate DataFrame: {parsed_data['message']}")
        daily_or_monthly = parsed_data["daily_or_monthly"]
        data = parsed_data["data"]
        if daily_or_monthly == "daily":
            name = data["name"]["name"]
            timeline_data = data["timeline"]
            timeline_df = pd.DataFrame(timeline_data)
            timeline_df["name"] = name
            timeline_df = timeline_df[["name", "datetime", "event_name", "event_details"] + list(set(timeline_df.columns) - {"name", "datetime", "event_name", "event_details"})]
        if daily_or_monthly == "monthly":
            timeline_df = pd.DataFrame(columns=["name", "datetime", "event_name", "event_name_en", "group", "amount", "amount_int", "amount_unit", "poo_hardness", "poo_color", "event_details"])
            for daily_data in data:
                if daily_data["status"] == "invalid":
                    continue
                name = daily_data["name"]["name"]
                timeline_data = daily_data["timeline"]
                daily_df = pd.DataFrame(timeline_data)
                daily_df["name"] = name
                daily_df = daily_df[["name", "datetime", "event_name", "event_details"] + list(set(daily_df.columns) - {"name", "datetime", "event_name", "event_details"})]
                timeline_df = pd.concat([timeline_df, daily_df], ignore_index=True)
        timeline_df = timeline_df[
            [
                "name",
                "datetime",
                "event_name",
                "event_name_en",
                "group",
                "amount",
                "amount_int",
                "amount_unit",
                "poo_hardness",
                "poo_color",
                "event_details",
            ]
        ]
        return timeline_df


if __name__ == "__main__":
    parser = PiyologParser()
    parsed_json = parser.parse("tests/data/invalid/monthly/invalid_separator3.txt")
    print(json.dumps(parsed_json, indent=4, ensure_ascii=False))
    if parsed_json["status"] == "valid":
        parsed_df = parser.get_timeline_df(parsed_json)
        print(parsed_df)
