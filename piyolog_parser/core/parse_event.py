import json
import re
from pathlib import Path
import warnings


class ParserEvent:
    def __init__(self):
        base_path = Path(__file__).resolve().parent.parent
        events_path = base_path / "data/events.json"
        with open(events_path) as f:
            self.events = json.load(f)

    def parse(self, event: dict):
        """
        Parse event data and collect warnings.
        """
        warnings_list = []

        try:
            event_name = event["event_name"]
            event_group = self.events.get(event_name, {}).get("group", None)

            with warnings.catch_warnings(record=True) as caught_warnings:
                warnings.simplefilter("always")

                if event_group == "drink":
                    parsed_event = self.parse_drink(event)
                elif event_group == "peepoo":
                    parsed_event = self.parse_peepoo(event)
                elif event_group == "sleep":
                    parsed_event = self.parse_sleep(event)
                elif event_group == "eat":
                    parsed_event = self.parse_eat(event)
                elif event_group == "other":
                    parsed_event = self.parse_other(event)
                else:
                    parsed_event = event

                # 警告をリストに追加
                for w in caught_warnings:
                    warnings_list.append(str(w.message))

            parsed_event["warnings"] = warnings_list  # 警告をイベントに追加
            return parsed_event

        except Exception as e:
            return {"status": "invalid", "message": str(e)}

    def parse_drink(self, event: dict):
        event_name = event["event_name"]
        event_details = event["event_details"]
        event_name_en = self.events.get(event_name, {}).get("name_en", None)
        match = re.search(r"(-?\d+)ml", event_details)
        amount_int = None
        if match:
            try:
                amount_int = int(match.group(1))
                if amount_int < 0:
                    amount_int = None
                    warnings.warn(f"amount may be invalid: {event_details}", UserWarning)
            except ValueError:
                warnings.warn(f"amount may be invalid: {event_details}", UserWarning)

        event["event_name_en"] = event_name_en
        event["group"] = "drink"
        event["amount"] = None
        if amount_int:
            event["amount"] = f"{amount_int}ml"
        event["amount_int"] = amount_int
        event["amount_unit"] = "ml"
        return event

    def parse_peepoo(self, event: dict):
        event_name = event["event_name"]
        event_details = event["event_details"]
        event_name_en = self.events.get(event_name, {}).get("name_en", None)
        if event_name_en == "poo":
            pattern = re.compile(r"\(([^)]+)\)\s*(.*)")
            match = pattern.match(event_details)
            amount, hardness, color, amount_int = None, None, None, None
            if match:
                attributes = match.group(1).split("/")
                attributes = [attr.replace("(", "") for attr in attributes]

                for attr in attributes:
                    if amount is None and attr in self.events["うんち"]["amount"]:
                        amount = attr
                        amount_int = int(self.events["うんち"]["amount"][amount]["amount_int"])
                    elif hardness is None and attr in self.events["うんち"]["poo_hardness"]:
                        hardness = attr
                    elif color is None and attr in self.events["うんち"]["poo_color"]:
                        color = attr

            event["event_name_en"] = event_name_en
            event["group"] = "peepoo"
            event["amount"] = amount
            event["poo_hardness"] = hardness
            event["poo_color"] = color
            event["amount_int"] = amount_int
            event["amount_unit"] = "g"
        elif event_name_en == "pee":
            event["event_name_en"] = event_name_en
            event["group"] = "peepoo"
        return event

    def parse_sleep(self, event: dict):
        event_name = event["event_name"]
        event_details = event["event_details"]
        event_name_en = self.events.get(event_name, {}).get("name_en", None)
        if event_name_en == "wakeup":
            duration_pattern = re.compile(r"\((?:(\d+)時間)?(?:(\d+)分)?\)")
            match = duration_pattern.match(event_details)
            if match:
                hours = int(match.group(1)) if match.group(1) else 0
                if hours < 0 or hours > 24:
                    hours = 0
                    warnings.warn(f"hours may be invalid: {event_details}", UserWarning)
                minutes = int(match.group(2)) if match.group(2) else 0
                if minutes < 0 or minutes > 59:
                    minutes = 0
                    warnings.warn(f"minutes may be invalid: {event_details}", UserWarning)

                amount = f"{hours}時間{minutes}分"
                amount_int = int(hours * 60 + minutes)
                event["amount"] = amount
                event["amount_int"] = amount_int
                event["amount_unit"] = "min"

        event["event_name_en"] = event_name_en
        event["group"] = "sleep"
        return event

    def parse_eat(self, event: dict):
        event_name = event["event_name"]
        event_name_en = self.events.get(event_name, {}).get("name_en", None)
        event["event_name_en"] = event_name_en
        event["group"] = "eat"
        return event

    def parse_other(self, event: dict):
        event_name = event["event_name"]
        event_name_en = self.events.get(event_name, {}).get("name_en", None)
        event["event_name_en"] = event_name_en
        event["group"] = "other"
        return event


if __name__ == "__main__":
    parser = ParserEvent()

    test_events = [
        {"datetime": "2025/2/3 08:00", "event_name": "搾母乳", "event_details": "120ml"},
        {"datetime": "2025/2/3 08:00", "event_name": "うんち", "event_details": "(ふつう/ふつう)"},
        {"datetime": "2025/2/3 08:00", "event_name": "ミルク", "event_details": "210l"},
        {"datetime": "2025/2/3 08:00", "event_name": "ミルク", "event_details": "-210ml"},
    ]

    for event in test_events:
        print(json.dumps(parser.parse(event), indent=4, ensure_ascii=False))
