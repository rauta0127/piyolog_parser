import json
import re


class ParserEvent:
    def __init__(self):
        with open("/Users/takuma.urata/Desktop/z/piyolog_parser/piyolog_parser/core/events.json") as f:
            self.events = json.load(f)

    def parse(self, event: dict):
        event_name = event["event_name"]
        event_group = self.events.get(event_name, {}).get("group", None)

        if event_group == "drink":
            return self.parse_drink(event)
        if event_group == "peepoo":
            return self.parse_peepoo(event)
        if event_group == "sleep":
            return self.parse_sleep(event)
        if event_group == "other":
            return self.parse_sleep(event)
        return event

    def parse_drink(self, event: dict):
        event_name = event["event_name"]
        event_details = event["event_details"]
        event_name_en = self.events.get(event_name, {}).get("name_en", None)
        match = re.search(r"(\d+)ml", event_details)
        amount_int = int(match.group(1)) if match else 0
        event["event_name_en"] = event_name_en
        event["group"] = "drink"
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
                # free_text = match.group(2).strip() if match.group(2) else ""

                for attr in attributes:
                    if amount is None and attr in self.events["うんち"]["amount"]:
                        amount = attr
                        amount_int = int(self.events["うんち"]["amount"][amount]["amount_int"])
                    elif hardness is None and attr in self.events["うんち"]["hardness"]:
                        hardness = attr
                    elif color is None and attr in self.events["うんち"]["color"]:
                        color = attr

            event["event_name_en"] = event_name_en
            event["group"] = "peepoo"
            event["amount"] = amount
            event["hardness"] = hardness
            event["color"] = color
            event["amount_int"] = amount_int
            event["amount_unit"] = "g"
        if event_name_en == "pee":
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
                minutes = int(match.group(2)) if match.group(2) else 0
                amount = f"{hours}時間{minutes}分"
                amount_int = int(hours * 60 + minutes)
                event["amount"] = amount
                event["amount_int"] = amount_int
                event["amount_unit"] = "min"

        event["event_name_en"] = event_name_en
        event["group"] = "sleep"
        return event

    def parse_other(self, event: dict):
        event_name = event["event_name"]
        # event_details = event["event_details"]
        event_name_en = self.events.get(event_name, {}).get("name_en", None)
        event["event_name_en"] = event_name_en
        event["group"] = "other"
        return event


if __name__ == "__main__":
    parser = ParserEvent()
    # event = {"datetime": "2025/2/3 08:00", "event_name": "うんち", "event_details": ""}
    # print(parser.parse_peepoo(event))

    event = {"datetime": "2025/2/3 08:00", "event_name": "搾母乳", "event_details": "120ml"}
    print(parser.parse(event))

    event = {"datetime": "2025/2/3 08:00", "event_name": "うんち", "event_details": "(ふつう/ふつう)"}
    print(parser.parse(event))
