# 👶 piyolog_parser

**piyolog_parser** is a Python package that structures log text data from the childcare record app **Piyolog**.  
It supports both **daily and monthly logs**, converting them into **JSON** or **Pandas DataFrame** formats for easy analysis and visualization.

## 🍼 Install
```sh
pip install piyolog_parser
```
🚧 Currently preparing for PyPI registration.

## 🚀 Features
- **Parse Piyolog text logs** into structured data
- Supports **both daily and monthly logs**
- Converts to **JSON or Pandas DataFrame**
- Helps with **tracking baby activities (sleep, feeding, diaper changes, etc.)**
- Can be used for **data analysis and visualization**

### to JSON
```python
from piyolog_parser.parser import PiyologParser

parser = PiyologParser()
piyolog_textfile = "Piyolog_sample_20250203.txt"
parsed_json = parser.parse(piyolog_textfile)
print(parsed_json)
```

#### Sample Output
```bash
{
    "status": "valid",
    "daily_or_monthly": "daily",
    "data": {
        "title": {
            "date": "2025/2/4",
            "weekday": "火"
        },
        "name": {
            "name": "ぴよこ",
            "age": "0歳8か月15日"
        },
        "timeline": [
            {
                "datetime": "2025/2/4 06:10",
                "event_name": "起きる",
                "event_details": "(8時間20分)",
                "amount": "8時間20分",
                "amount_int": 500,
                "amount_unit": "min",
                "event_name_en": "wakeup",
                "group": "sleep"
            },
            {
                "datetime": "2025/2/4 06:40",
                "event_name": "ミルク",
                "event_details": "210ml",
                "event_name_en": "milk",
                "group": "drink",
                "amount": "210ml",
                "amount_int": 210,
                "amount_unit": "ml"
            },
            {
                "datetime": "2025/2/4 07:30",
                "event_name": "おしっこ",
                "event_details": "",
                "event_name_en": "pee",
                "group": "peepoo"
            },
            {
                "datetime": "2025/2/4 07:30",
                "event_name": "うんち",
                "event_details": "(多め/ふつう) 漏れた",
                "event_name_en": "poo",
                "group": "peepoo",
                "amount": "多め",
                "poo_hardness": "ふつう",
                "poo_color": null,
                "amount_int": 50,
                "amount_unit": "g"
            }
        ]
    }
}
```

### to DataFrame
```python
from piyolog_parser.parser import PiyologParser

parser = PiyologParser()
piyolog_textfile = "Piyolog_sample_20250203.txt"
parsed_json = parser.parse(piyolog_textfile)
parsed_df = parser.get_timeline_df(parsed_json)
print(parsed_df)
```

#### Sample Output
```markdown
   name        datetime event_name event_name_en   group  amount  amount_int amount_unit poo_hardness  poo_color event_details
0   ぴよこ  2025/2/4 06:10        起きる        wakeup   sleep  8時間20分       500.0         min          NaN        NaN      (8時間20分)
1   ぴよこ  2025/2/4 06:40        ミルク          milk   drink   210ml       210.0          ml          NaN        NaN         210ml
2   ぴよこ  2025/2/4 07:30       おしっこ           pee  peepoo     NaN         NaN         NaN          NaN        NaN              
3   ぴよこ  2025/2/4 07:30        うんち           poo  peepoo      多め        50.0           g          ふつう        NaN  (多め/ふつう) 漏れた
```

## ⚠️ Disclaimer
This project, `piyolog_parser`, is an **independent open-source project** and is **not affiliated with, endorsed by, or associated with Piyolog or its developers**.  
It simply provides a tool to **structure Piyolog log text files into JSON/Pandas DataFrame format**.


### Reference
- [ぴよログ](https://www.piyolog.com/)