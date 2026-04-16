import httpx
from datetime import date, timedelta
from pytrends.request import TrendReq
from app.config import settings
from sqlalchemy.orm import Session
from app.models.collection.trends import Trend, TopicType

# DB에서 동적으로 구성할 예정. 임시 하드코딩.
KEYWORDS = {
    "BUSINESS": ["SaaS", "B2B", "스타트업", "핀테크"],
    "TECH": ["AI", "LLM", "자동화"],
    "SOCIAL": ["쇼츠", "부업", "워라밸"],
}


def crawl_trends(db: Session) -> None:
    """Google Trends + 네이버 DataLab에서 트렌드 점수 수집 → TRENDS 저장."""
    today = date.today()
    pytrend = TrendReq(hl="ko", tz=540)  # 커넥션 한 번만 생성
    for topic_type, kw_list in KEYWORDS.items():
        for keyword in kw_list:
            google_score = _fetch_google_trends(keyword, pytrend)
            naver_score = _fetch_naver_datalab(keyword)
            _save_trend(db, keyword, topic_type, today, google_score, "google_trends")
            _save_trend(db, keyword, topic_type, today, naver_score, "naver_datalab")


def _fetch_google_trends(keyword: str, pytrend: TrendReq) -> float | None:
    pytrend.build_payload([keyword], timeframe="today 7-d")
    df = pytrend.interest_over_time()
    return df[keyword].mean() if not df.empty else None


def _fetch_naver_datalab(keyword: str) -> float | None:
    NAVER_CLIENT_ID = settings.NAVER_CLIENT_ID
    NAVER_CLIENT_SECRET = settings.NAVER_CLIENT_SECRET

    with httpx.Client() as client:
      response = client.post(
        "https://openapi.naver.com/v1/datalab/search",
        headers={
          "X-Naver-Client-Id": NAVER_CLIENT_ID,
          "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
          "Content-Type": "application/json"
        },
        json={
          "startDate": (date.today() - timedelta(days=7)).strftime("%Y-%m-%d"),
          "endDate": date.today().strftime("%Y-%m-%d"),
          "timeUnit": "date",
          "keywordGroups": [{
            "groupName": keyword,
            "keywords": [keyword]
          }]
        }
      )
    data = response.json()["results"][0]["data"]
    avg = sum(d["ratio"] for d in data)/len(data)
    return avg


def _save_trend(db: Session, keyword: str, topic_type: str, trend_date: date, score: float | None, source: str) -> None:
    db.add(Trend(
        topic=keyword,
        topic_type=TopicType(topic_type),
        trend_date=trend_date,
        trend_score=score,
        source=source,
        # summary: 추후 Claude 요약 붙일 때 채울 예정
    ))
    db.commit()
