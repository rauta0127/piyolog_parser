import pytest
from pathlib import Path
from piyolog_parser.parser import PiyologParser

TEST_DATA_DIR = Path(__file__).parent / "data"


@pytest.mark.parametrize(
    "filename, expected_status",
    [
        ("valid/daily/valid_daily.txt", "valid"),
        ("valid/monthly/valid_monthly.txt", "valid"),
        ("invalid/daily/contain_other_strings.txt", "invalid"),
        ("invalid/daily/empty_file.txt", "invalid"),
        ("invalid/daily/empty_header.txt", "invalid"),
        ("invalid/daily/empty_name.txt", "invalid"),
        ("invalid/daily/invalid_date_format.txt", "invalid"),
        ("invalid/daily/invalid_date.txt", "invalid"),
        ("invalid/daily/invalid_format.txt", "invalid"),
        ("invalid/daily/invalid_header1.txt", "invalid"),
        ("invalid/daily/invalid_header2.txt", "invalid"),
        ("invalid/daily/invalid_time.txt", "invalid"),
        ("invalid/daily/missing_event_name.txt", "valid"),  # TODO: 結果はvalidで良いが、イベント名が空であることのWARNINGが出るようにしたい
        ("invalid/daily/missing_name.txt", "invalid"),
        ("invalid/daily/missing_time.txt", "invalid"),
        ("invalid/daily/negative_values.txt", "valid"),  # TODO: 結果はvalidで良いが、量がマイナスであることのWARNINGが出るようにしたい
        ("invalid/daily/unexpected_symbols.txt", "valid"),  # TODO: 結果はvalidで良いが、余計な文字が含まれていることのWARNINGが出るようにしたい
        ("invalid/monthly/empty_file.txt", "invalid"),
        ("invalid/monthly/empty_header.txt", "invalid"),
        ("invalid/monthly/invalid_name.txt", "valid"),  # TODO: 結果はvalidで良いが、名前が空であることのWARNINGが出るようにしたい
        ("invalid/monthly/invalid_separator1.txt", "invalid"),
        ("invalid/monthly/invalid_separator2.txt", "invalid"),
        ("invalid/monthly/invalid_separator3.txt", "invalid"),
        # ("invalid/monthly/notequal_month.txt", "invalid"),
    ],
)
def test_parse_with_various_invalid_files(filename, expected_status):
    parser = PiyologParser()
    parsed_data = parser.parse(str(TEST_DATA_DIR / filename))
    assert parsed_data["status"] == expected_status
