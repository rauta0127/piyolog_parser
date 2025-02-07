import re
import pandas as pd
from datetime import datetime
import warnings
from .parse_base import ParserBase
from .parse_event import ParserEvent


class ParserDaily(ParserBase):
    def __init__(self):
        pass

    def parse_block(self, lines: list) -> dict:
        blocks = {}
        block_title_idx = 0
        block_name_idx = 1
        block_timeline_idx_list = []
        block_stats_idx_list = []
        block_diary_idx_list = []

        name_pattern = re.compile(r"(.+?)\(\s*(\d+歳\d+か月\d+日)\)")

        for i, line in enumerate(lines):
            if line == "\n":
                continue
            if re.match(r"(?:【ぴよログ】)?(\d{4}/\d{1,2}/\d{1,2})\((.+)\)", line):
                block_title_idx = i
            elif name_pattern.match(line):
                block_name_idx = i
            elif re.match(r"\d{2}:\d{2}", line):
                block_timeline_idx_list.append(i)
            elif "合計" in line:
                block_stats_idx_list.append(i)
            elif len(block_stats_idx_list) > 0:
                block_diary_idx_list.append(i)

        blocks["title"] = lines[block_title_idx].replace("\n", "")
        blocks["name"] = lines[block_name_idx].replace("\n", "")
        blocks["timeline"] = [lines[i].replace("\n", "") for i in block_timeline_idx_list]
        blocks["stats"] = [lines[i].replace("\n", "") for i in block_stats_idx_list]
        blocks["diary"] = [lines[i].replace("\n", "") for i in block_diary_idx_list]

        return blocks

    def parse_title_block(self, title_block: str) -> dict:
        """
        parse title block
        """
        title_pattern = re.compile(r"(?:【ぴよログ】)?(\d{4}/\d{1,2}/\d{1,2})\((.+)\)")
        match = title_pattern.match(title_block)

        if match:
            date_str = match.group(1)
            weekday = match.group(2)

            # 日付の妥当性チェック
            try:
                datetime.strptime(date_str, "%Y/%m/%d")
            except ValueError:
                raise ValueError(f"Invalid date: {date_str}")

            return {"date": date_str, "weekday": weekday}
        raise ValueError(f"Invalid title block: {title_block}")

    def parse_name_block(self, name_block: str) -> dict:
        """
        parse name block
        """
        name_pattern = re.compile(r"(.+?)\(\s*(\d+歳\d+か月\d+日)\)")
        match = name_pattern.match(name_block)

        if match:
            name = match.group(1).strip()
            age = match.group(2)
            if name == "":
                warnings.warn(f"Name is blank: {name_block}", UserWarning)
            return {"name": name, "age": age}
        raise ValueError(f"Invalid name block: {name_block}")

    def parse_timeline(self, timeline: list, parsed_title_block: dict) -> list:
        """
        Parse timeline block
        """
        time_pattern = re.compile(r"^(\d{2}:\d{2})\s+([^\s]+)(?:\s+(.+))?")
        parsed_timeline = []
        date = parsed_title_block["date"]

        for entry in timeline:
            match = time_pattern.match(entry)
            if match:
                time = match.group(1)
                datetime_str = f"{date} {time}"
                try:
                    datetime.strptime(datetime_str, "%Y/%m/%d %H:%M")
                except ValueError:
                    raise ValueError(f"Invalid datetime: {datetime_str}")
                event_name = match.group(2)
                if event_name == "":
                    warnings.warn(f"Event Name is blank: {entry}", UserWarning)
                event_details = match.group(3) if match.group(3) else ""
                event = {"datetime": datetime_str, "event_name": event_name, "event_details": event_details}
                parser_event = ParserEvent()
                parsed_event = parser_event.parse(event)
                parsed_timeline.append(parsed_event)

        if len(parsed_timeline) == 0:
            raise ValueError("No valid timeline entries")
        return parsed_timeline

    def parse(self, lines: list):
        """
        parse daily lines
        """
        if len(lines) == 0:
            return {"status": "invalid", "message": "empty file"}
        if len(lines) < 4:
            return {"status": "invalid", "message": "invalid as piyolog format (Too short)"}

        warnings_list = []  # 警告を収集するリスト
        try:
            blocks = self.parse_block(lines)

            # 警告をキャッチするコンテキスト
            with warnings.catch_warnings(record=True) as caught_warnings:
                warnings.simplefilter("always")  # すべての警告をキャッチ

                title = self.parse_title_block(blocks["title"])
                name = self.parse_name_block(blocks["name"])
                timeline = self.parse_timeline(blocks["timeline"], title)

                # キャッチした警告をリストに追加
                for w in caught_warnings:
                    warnings_list.append(str(w.message))

            return {
                "status": "valid",
                "title": title,
                "name": name,
                "timeline": timeline,
                "warnings": warnings_list,  # 警告があればリストに含める
            }

        except ValueError as e:
            return {"status": "invalid", "message": str(e)}

    def convert_timeline_to_dataframe(self, data: dict) -> pd.DataFrame:
        name = data["name"]["name"]
        timeline_data = data["timeline"]
        timeline_df = pd.DataFrame(timeline_data)
        timeline_df["name"] = name
        timeline_df = timeline_df[["name", "datetime", "event_name", "event_details"] + list(set(timeline_df.columns) - {"name", "datetime", "event_name", "event_details"})]
        return timeline_df


if __name__ == "__main__":
    with open("tests/data/invalid/daily/missing_time.txt") as f:
        lines = f.readlines()
    parser = ParserDaily()
    parsed_data = parser.parse(lines)
    print(parsed_data)
    if parsed_data["status"] == "valid":
        timeline_df = parser.convert_timeline_to_dataframe(parsed_data)
        print(timeline_df)
