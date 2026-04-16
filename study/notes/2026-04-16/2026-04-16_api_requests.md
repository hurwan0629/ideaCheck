# 2026-04-16 | 외부 API 요청 방법 (pytrends / Naver DataLab)

## httpx.Client — 동기 HTTP 요청

```python
import httpx

with httpx.Client() as client:
    response = client.get("https://example.com/api", params={"q": "keyword"})
    response = client.post("https://example.com/api", json={"key": "value"}, headers={"Authorization": "Bearer ..."})

response.status_code   # 200
response.json()        # dict
response.text          # 문자열
```

- `with` 블록 → 요청 끝나면 커넥션 자동 정리 (Spring의 try-with-resources)
- `params=` → URL 쿼리스트링 자동 인코딩 (?q=keyword)
- `json=` → Content-Type: application/json 자동 설정 + dict 직렬화


---

## pytrends — Google Trends (비공식)

> Google이 공식 API를 제공 안 해서 브라우저 요청을 흉내내는 라이브러리.

```python
from pytrends.request import TrendReq

pytrend = TrendReq(hl="ko", tz=540)
# hl: 언어, tz: 타임존 오프셋 (한국 UTC+9 = 540분)

pytrend.build_payload(["SaaS"], timeframe="today 1-m")
# "이 키워드로 최근 1달 데이터 줘" — 실제 요청은 아직 안 함

df = pytrend.interest_over_time()
# 여기서 실제 요청 실행. pandas DataFrame 반환
# index: 날짜, 컬럼: 키워드명 + "isPartial"
# 값: 0~100 상대 점수 (100 = 해당 기간 최고 관심도)

score = float(df["SaaS"].iloc[-1])  # 가장 최근 날짜 값
```

**주의**: 비공식이라 요청 너무 빠르게 보내면 429 차단.
키워드 여러 개 돌릴 때 `time.sleep(1)` 권장.


---

## Naver DataLab — 공식 REST API

> 네이버 검색량 트렌드. [네이버 개발자센터](https://developers.naver.com) 앱 등록 후 키 발급 필요.

```python
import httpx
from datetime import date

with httpx.Client() as client:
    response = client.post(
        "https://openapi.naver.com/v1/datalab/search",
        headers={
            "X-Naver-Client-Id": "CLIENT_ID",
            "X-Naver-Client-Secret": "CLIENT_SECRET",
            "Content-Type": "application/json",
        },
        json={
            "startDate": "2024-01-01",
            "endDate": date.today().strftime("%Y-%m-%d"),
            "timeUnit": "date",       # "date" | "week" | "month"
            "keywordGroups": [
                {
                    "groupName": "SaaS",       # 결과에서 이 이름으로 식별
                    "keywords": ["SaaS", "saas"],  # 동의어 묶기 가능
                }
            ],
        },
    )

data = response.json()
# {
#   "results": [
#     {
#       "title": "SaaS",
#       "data": [
#         {"period": "2024-01-01", "ratio": 45.2},
#         {"period": "2024-01-02", "ratio": 50.0},
#         ...
#       ]
#     }
#   ]
# }

score = data["results"][0]["data"][-1]["ratio"]  # 가장 최근 ratio
```

**ratio**: 0~100 상대 점수 (Google Trends와 동일한 개념, 기간 내 최고값 기준).


---

## 두 API 비교

| | Google Trends (pytrends) | Naver DataLab |
|---|---|---|
| 공식 여부 | 비공식 | 공식 |
| 인증 | 없음 | Client ID / Secret |
| 안정성 | 차단 가능 (429) | 안정적 |
| 커버리지 | 전 세계 구글 검색 | 네이버 검색 한정 |
| 응답 형식 | pandas DataFrame | JSON |


---

## 불명확한 것

- pytrends 429 차단 시 대응 (프록시? 재시도 로직?)
- Naver DataLab `keywordGroups` 최대 개수 제한
