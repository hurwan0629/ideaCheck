from dotenv import load_dotenv
import os
import httpx
import json
from pathlib import Path

load_dotenv()

_NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
_NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")

_url = "https://openapi.naver.com/v1/search/news.json"

headers = {
  "X-Naver-Client-Id": _NAVER_CLIENT_ID,
  "X-Naver-Client-Secret": _NAVER_CLIENT_SECRET
}

params = {
  "query": "OpenAI",
  "display": 10,
  "start": 1,
  "sort": "sim"
}

def test():
  with httpx.Client(timeout=10.0) as client:
    response = client.get(
      _url,
      headers=headers,
      params=params
    )
    test_path = Path(__file__).resolve().parent / "test"
    test_path.mkdir(parents=True, exist_ok=True)

    test_json = test_path / "test.json"
    with test_json.open("w", encoding="utf-8") as f:
      print(response.status_code)
      json.dump(response.json(), f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
  test()