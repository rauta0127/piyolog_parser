import re
from .parse_base import ParserBase
from .parse_daily import ParserDaily


class ParserMonthly(ParserDaily):
    def __init__(self):
        pass

    def split_daily_blocks(self, lines: list) -> dict:
        separators_idx_list = []
        for i, line in enumerate(lines):
            if i > 0:
                if re.match(r"^-{10,}$", line) and lines[i - 1] == "\n":
                    separators_idx_list.append(i)

        daily_blocks = []
        for i, idx in enumerate(separators_idx_list):
            if i < len(separators_idx_list) - 1:
                start_idx = idx + 1
                end_idx = separators_idx_list[i + 1] - 2
                daily_blocks.append(lines[start_idx:end_idx])

        return daily_blocks


if __name__ == "__main__":
    parser = ParserMonthly()
    with open("data/Piyolog_Hinano_202409.txt") as f:
        lines = f.readlines()
    daily_blocks = parser.split_daily_blocks(lines)
    for daily_block in daily_blocks:
        print(parser.parse(daily_block))
        print("****************")
