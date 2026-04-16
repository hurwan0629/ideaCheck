import httpx
from datetime import date

# DB에서 동적으로 구성할 예정. 임시 하드코딩.
KEYWORDS = {
    "BUSINESS": ["SaaS", "B2B", "스타트업", "핀테크"],
    "TECH": ["AI", "LLM", "자동화"],
    "SOCIAL": ["쇼츠", "부업", "워라밸"],
}


def crawl_trends() -> None:
    """Google Trends + 네이버 DataLab에서 트렌드 점수 수집 → TRENDS 저장."""
    today = date.today()
    for topic_type, kw_list in KEYWORDS.items():
        for keyword in kw_list:
            google_score = _fetch_google_trends(keyword)
            naver_score = _fetch_naver_datalab(keyword)
            _save_trend(keyword, topic_type, today, google_score, "google_trends")
            _save_trend(keyword, topic_type, today, naver_score, "naver_datalab")


def _fetch_google_trends(keyword: str) -> float | None:
    # pytrends는 동기 라이브러리라 그대로 사용 가능
    # TODO: pytrends 실제 호출
    # from pytrends.request import TrendReq
    # pytrend = TrendReq(hl="ko", tz=540)
    # pytrend.build_payload([keyword], timeframe="today 1-m")
    # df = pytrend.interest_over_time()
    # return float(df[keyword].iloc[-1]) if not df.empty else None
    return None


def _fetch_naver_datalab(keyword: str) -> float | None:
    # TODO: 네이버 DataLab API 실제 호출
    # with httpx.Client() as client:
    #     response = client.post(
    #         "https://openapi.naver.com/v1/datalab/search",
    #         headers={"X-Naver-Client-Id": "...", "X-Naver-Client-Secret": "...", "Content-Type": "application/json"},
    #         json={
    #             "startDate": "2024-01-01",
    #             "endDate": date.today().strftime("%Y-%m-%d"),
    #             "timeUnit": "date",
    #             "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}],
    #         },
    #     )
    #     return response.json()["results"][0]["data"][-1]["ratio"]
    return None


def _save_trend(keyword: str, topic_type: str, trend_date: date, score: float | None, source: str) -> None:
    # TODO: DB 세션 열어서 UPSERT (TOPIC + TREND_DATE + SOURCE 조합 중복 방지)
    pass
