import pandas as pd

from .parse_base import ParserBase
from .parse_daily import ParserDaily
from .parse_monthly import ParserMonthly


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
        else:
            with open(filepath) as f:
                lines = f.readlines()
            if daily_or_monthly == "daily":
                parser = ParserDaily()
                data = parser.parse(lines)
                return {"status": "valid", "daily_or_monthly": "daily", "data": data}
            if daily_or_monthly == "monthly":
                parser = ParserMonthly()
                daily_blocks = parser.split_daily_blocks(lines)
                data = []
                parser = ParserDaily()
                for daily_block in daily_blocks:
                    data.append(parser.parse(daily_block))
                return {"status": "valid", "daily_or_monthly": "monthly", "data": data}

    def get_timeline_df(self, data, daily_or_monthly) -> pd.DataFrame:
        if daily_or_monthly == "daily":
            name = data["name"]["name"]
            timeline_data = data["timeline"]
            timeline_df = pd.DataFrame(timeline_data)
            timeline_df["name"] = name
            timeline_df = timeline_df[["name", "datetime", "event_name", "event_details"]]
        if daily_or_monthly == "monthly":
            timeline_df = pd.DataFrame()
            for daily_data in data:
                name = daily_data["name"]["name"]
                timeline_data = daily_data["timeline"]
                daily_df = pd.DataFrame(timeline_data)
                daily_df["name"] = name
                daily_df = daily_df[["name", "datetime", "event_name", "event_details"]]
                timeline_df = pd.concat([timeline_df, daily_df], ignore_index=True)
        return timeline_df


if __name__ == "__main__":
    parser = PiyologParser()
    parsed_data = parser.parse("data/Piyolog_Hinano_202501.txt")
    daily_or_monthly = parsed_data["daily_or_monthly"]
    data = parsed_data["data"]
    timeline_df = parser.get_timeline_df(data, daily_or_monthly)
    print(timeline_df)
