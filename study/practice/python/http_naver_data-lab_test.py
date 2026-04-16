import httpx
from datetime import date
import json

import os
from dotenv import load_dotenv

load_dotenv()

NAVER_CLIENT_ID=os.getenv("X-Naver-Client-Id", "no_id")
NAVER_SECRET=os.getenv("X-Naver-Client-Secret", "no_secret")

print(NAVER_CLIENT_ID)
print(NAVER_SECRET)

with httpx.Client() as client:
  response = client.post(
    "https://openapi.naver.com/v1/datalab/search",
    headers={
      "X-Naver-Client-Id": NAVER_CLIENT_ID,
      "X-Naver-Client-Secret": NAVER_SECRET,
      "Content-Type": "application/json"
    },
    json={
      "startDate": "2026-01-01",
      "endDate": date.today().strftime("%Y-%m-%d"),
      "timeUnit": "date",
      "keywordGroups": [{
        "groupName": "SaaS",
        "keywords": ["SaaS"]
      }]
    }
  )

  print(response.status_code)
  print(json.dumps(response.json(), indent=2, ensure_ascii=False))