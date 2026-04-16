import httpx
from config import settings
import json

naver_id = settings.NAVER_CLIENT_ID
naver_secret = settings.NAVER_CLIENT_SECRET

print(f"naver_id: " + naver_id)
print(f"naver_secret: " + naver_secret)

with httpx.Client() as client:
  response = client.get(
    "https://openapi.naver.com/v1/search/news.json",
    headers={
      "X-Naver-Client-Id": naver_id,
      "X-Naver-Client-Secret": naver_secret,
      "Content-Type": "application/json"
    },
    params={
      "query": "코스피",
      "display": 5,
      "sort": "date"
    }
  )

  print(f"response타입: {type(response)}")
  data = response.json()
  print(json.dumps(response.json(), indent=2, ensure_ascii=False))
  """
  for item in data["items"]:
    print(item["title"])
    print(item["pubDate"])
    print(item["link"])
    print("="*20)
    """