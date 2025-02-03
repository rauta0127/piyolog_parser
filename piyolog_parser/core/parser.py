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
                return {"status": "valid", "data": data}
            if daily_or_monthly == "monthly":
                parser = ParserMonthly()
                daily_blocks = parser.split_daily_blocks(lines)
                data = []
                parser = ParserDaily()
                for daily_block in daily_blocks:
                    data.append(parser.parse(daily_block))
                return {"status": "valid", "data": data}

    # def parse_to_pandas(self, filepath: str) -> pd.DataFrame:
    #     with open(self.path) as f:
    #         lines = f.readlines()

    #     df = pd.DataFrame(columns=["date", "time", "level", "message"])
    #     for line in lines:
    #         date, time, level, message = self._parse_line(line)
    #         df = df.append({"date": date, "time": time, "level": level, "message": message}, ignore_index=True)
    #     return df


if __name__ == "__main__":
    parser = PiyologParser()
    print(parser.parse("data/Piyolog_Hinano_202501.txt"))
