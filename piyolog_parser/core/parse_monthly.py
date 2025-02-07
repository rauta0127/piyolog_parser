import re
import warnings
from .parse_base import ParserBase
from .parse_daily import ParserDaily


class ParserMonthly(ParserDaily):
    def __init__(self):
        pass

    def split_daily_blocks(self, lines: list) -> dict:
        if len(lines) == 0:
            return {"status": "invalid", "message": "empty file"}
        if not lines[0].startswith("【ぴよログ】"):
            return {"status": "invalid", "message": "invalid as piyolog format (missing header)"}

        separators_idx_list = []
        invalid_separators = []  # 短すぎるセパレーターの位置
        missing_separators = []  # 日付間にセパレーターがない位置
        date_pattern = re.compile(r"\d{4}/\d{1,2}/\d{1,2}")
        separator_pattern = re.compile(r"^-{10,}$")  # 10文字以上の `-` のみ

        for i, line in enumerate(lines):
            if i > 0:
                if separator_pattern.match(line) and lines[i - 1] == "\n":
                    separators_idx_list.append(i)
                elif re.match(r"^-{1,9}$", line):  # 10文字未満のセパレーターは無効
                    invalid_separators.append(i)

        # 不正なセパレーターがある場合、エラーとして処理
        if invalid_separators:
            warnings.warn(f"Invalid separator(s) detected at line(s): {invalid_separators}", UserWarning)
            return {"status": "invalid", "message": f"invalid separator(s) at line(s) {invalid_separators}"}

        # セパレーターが1つもない場合はエラー
        if not separators_idx_list:
            return {"status": "invalid", "message": "missing separators"}

        # 日付の前にセパレーターがないかチェック
        for i, line in enumerate(lines):
            if date_pattern.match(line):
                # 前の行が空白 (`\n`) で、その前の行がセパレーター (`----------`) でない場合をエラーにする
                if i > 1 and lines[i - 1] == "\n" and not separator_pattern.match(lines[i - 2]):
                    missing_separators.append(i)

        if missing_separators:
            return {"status": "invalid", "message": f"missing separators between dates at line(s) {missing_separators}"}

        # 正常な場合、日別にデータを分割
        daily_blocks = []
        for i, idx in enumerate(separators_idx_list):
            if i < len(separators_idx_list) - 1:
                start_idx = idx + 1
                end_idx = separators_idx_list[i + 1] - 2
                daily_blocks.append([l.replace("\n", "") for l in lines[start_idx:end_idx]])

        return {"status": "valid", "daily_blocks": daily_blocks}


if __name__ == "__main__":
    parser = ParserMonthly()
    with open("tests/data/valid/monthly/valid_monthly.txt") as f:
        lines = f.readlines()
    results = parser.split_daily_blocks(lines)

    if results["status"] == "invalid":
        print(results)
    if results["status"] == "valid":
        daily_blocks = results["daily_blocks"]
        for daily_block in daily_blocks:
            print(parser.parse(daily_block))
            print("****************")
