from typing import Any
from pathlib import Path
import json
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent
TEST_DIR= BASE_DIR / "test"

# print(json_files)

news_list: list[str] = []
count: int = 0

for file in sorted(TEST_DIR.glob("*.json")):
  with file.open("r", encoding="utf-8") as f:
    data = json.load(f)
    count += len(data.get("items", []))
    news_list += [obj.get("originallink", "") for obj in data["items"] if  obj.get("originallink")]
    print(file)
    print(len(data["items"]))
    print()

counter = [(k, v) for k, v in Counter(news_list).items() if v>1]
result = -len(counter)
for k, v in counter:
  result += v
for obj in counter:
  print(obj)
print(f"총 개수: {count}")
print(f"중복 개수: {len(counter)}")
print(f"제거된 중복: {result}")
print(f"중복 제거 후: {count-result}")