import json


class ParserEvent:
    def __init__(self):
        with open("events.json") as f:
            self.events = json.load(f)

    def parse(self, event: dict):
        event_name = event["event_name"]
        event_details = event["event_details"]
        event_group = self.events.get(event_name, {}).get("group", None)
        event_name_en = self.events.get(event_name, {}).get("name_en", None)

        if event_group == "drink":
            return self.parse_drink(event, event_name_en)
        return

    def parse_details(self, event_details: str):
        pass

    def parse_drink(self, event: dict, event_name_en: str):
        event_details = event["event_details"]
        if "を飲む" in event_details:
            drink = event_details.replace("を飲む", "")
            return {"drink": drink, "event_name_en": event_name_en}
        return
