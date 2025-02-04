import re
import pandas as pd
from .parse_base import ParserBase
from .parse_event import ParserEvent


class ParserDaily(ParserBase):
    def __init__(self):
        pass

    def parse_block(self, lines: list) -> dict:
        blocks = {}
        block_title_idx = 0
        block_name_idx = 0
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
            date = match.group(1)
            weekday = match.group(2)
            return {"date": date, "weekday": weekday}
        return {"date": date, "weekday": weekday}

    def parse_name_block(self, name_block: str) -> dict:
        """
        parse name block
        """
        name_pattern = re.compile(r"(.+?)\(\s*(\d+歳\d+か月\d+日)\)")
        match = name_pattern.match(name_block)

        if match:
            name = match.group(1).strip()
            age = match.group(2)
            return {"name": name, "age": age}
        return {"name": name, "age": age}

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
                datetime = f"{date} {time}"
                event_name = match.group(2)
                event_details = match.group(3) if match.group(3) else ""
                event = {"datetime": datetime, "event_name": event_name, "event_details": event_details}
                parser_event = ParserEvent()
                parsed_event = parser_event.parse(event)
                parsed_timeline.append(parsed_event)

        return parsed_timeline

    def parse(self, lines: list):
        """
        parse daily lines
        """
        blocks = self.parse_block(lines)
        title = self.parse_title_block(blocks["title"])
        name = self.parse_name_block(blocks["name"])
        timeline = self.parse_timeline(blocks["timeline"], title)
        return {"title": title, "name": name, "timeline": timeline}

    def convert_timeline_to_dataframe(self, data: dict) -> pd.DataFrame:
        name = data["name"]["name"]
        timeline_data = data["timeline"]
        timeline_df = pd.DataFrame(timeline_data)
        timeline_df["name"] = name
        timeline_df = timeline_df[["name", "datetime", "event_name", "event_details"] + list(set(timeline_df.columns) - {"name", "datetime", "event_name", "event_details"})]
        return timeline_df


if __name__ == "__main__":
    with open("data/Piyolog_Hinano_20250203_14.txt") as f:
        lines = f.readlines()
    parser = ParserDaily()
    parsed_data = parser.parse(lines)
    print(parsed_data)
    timeline_df = parser.convert_timeline_to_dataframe(parsed_data)
    print(timeline_df)
