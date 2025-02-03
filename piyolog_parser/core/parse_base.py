import re


class ParserBase:
    def __init__(self):
        pass

    def validate_piyolog_file(self, filepath: str) -> tuple[bool, str]:
        """
        check if the file is a valid piyolog file
        """
        if not filepath.endswith(".txt"):
            return False, "file extension is not .txt"
        with open(filepath) as f:
            lines = f.readlines()
            if len(lines) == 0:
                return False, "empty file"
            if not lines[0].startswith("【ぴよログ】"):
                return False, "invalid as piyolog format"
        return True, ""

    def check_daily_or_monthly(self, filepath: str) -> str:
        """
        check if the file is daily or monthly format
        """
        with open(filepath) as f:
            first_line = f.readline().strip()

            # Check for monthly format
            if re.match(r"【ぴよログ】\d{4}年\d{1,2}月", first_line):
                return "monthly"

            # Check for daily format
            if re.match(r"【ぴよログ】\d{4}/\d{1,2}/\d{1,2}\(.*\)", first_line):
                return "daily"

            return "unknown"


if __name__ == "__main__":
    parser = ParserBase()
    is_valid, message = parser.validate_piyolog_file("data/invalid.txt")
    print(is_valid, message)
    print(parser.check_daily_or_monthly("data/invalid.txt"))
