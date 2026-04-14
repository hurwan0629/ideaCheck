# 트렌드 데이터 수집.
# Google Trends, 네이버 DataLab 모두 API가 있어서 크롤링 없이 요청만 하면 됨.
# 이미 정제된 점수값을 반환하므로 RAW 테이블 없이 TRENDS에 바로 저장.
import httpx
from datetime import date, datetime

# pytrends: 비공식 Google Trends API 래퍼 라이브러리
# 공식 API가 없어서 비공식 라이브러리 사용 (불안정할 수 있음)
# 공식문서: https://github.com/GeneralMills/pytrends
# from pytrends.request import TrendReq  # 실제 사용 시 주석 해제


async def crawl_trends() -> None:
    """
    Google Trends + 네이버 DataLab에서 트렌드 점수 수집 → TRENDS 테이블 저장.
    매일 daily_job에서 호출.
    """
    today = date.today()

    # 수집할 키워드 목록 (실제로는 DB에서 IDEA_TOPIC_STATS 등을 참고해서 동적으로 구성)
    keywords = {
        "BUSINESS": ["SaaS", "B2B", "스타트업", "핀테크"],
        "TECH": ["AI", "LLM", "자동화"],
        "SOCIAL": ["쇼츠", "부업", "워라밸"],
    }

    for topic_type, kw_list in keywords.items():
        for keyword in kw_list:
            google_score = await _fetch_google_trends(keyword)
            naver_score = await _fetch_naver_datalab(keyword)

            # 두 소스를 별도 행으로 저장 (스케일이 달라서 합치면 안 됨)
            await _save_trend(keyword, topic_type, today, google_score, "google_trends")
            await _save_trend(keyword, topic_type, today, naver_score, "naver_datalab")


async def _fetch_google_trends(keyword: str) -> float | None:
    """
    Google Trends에서 키워드 점수 조회.
    반환값: 0~100 상대 점수 (해당 기간 내 최고값 대비 상대값)

    pytrends 사용 예시 (동기 라이브러리라 executor로 감싸야 함):
    공식문서: https://github.com/GeneralMills/pytrends#interest-over-time
    """
    # 실제 구현 예시:
    # import asyncio
    # loop = asyncio.get_event_loop()
    # pytrend = TrendReq(hl="ko", tz=540)  # tz=540 → 한국 시간대
    # await loop.run_in_executor(None, lambda: pytrend.build_payload([keyword], timeframe="today 1-m"))
    # df = await loop.run_in_executor(None, pytrend.interest_over_time)
    # return float(df[keyword].iloc[-1]) if not df.empty else None

    return None  # 구조 파악용 더미


async def _fetch_naver_datalab(keyword: str) -> float | None:
    """
    네이버 DataLab API에서 키워드 트렌드 점수 조회.
    반환값: 0~100 상대 점수

    API 신청: https://developers.naver.com/products/datalab/search/search.md
    """
    # 실제 구현 예시:
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(
    #         "https://openapi.naver.com/v1/datalab/search",
    #         headers={
    #             "X-Naver-Client-Id": "YOUR_CLIENT_ID",
    #             "X-Naver-Client-Secret": "YOUR_SECRET",
    #             "Content-Type": "application/json",
    #         },
    #         json={
    #             "startDate": "2024-01-01",
    #             "endDate": datetime.today().strftime("%Y-%m-%d"),
    #             "timeUnit": "date",
    #             "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}],
    #         },
    #     )
    #     data = response.json()
    #     # results[0]["data"][-1]["ratio"] → 가장 최근 날짜 점수
    #     return data["results"][0]["data"][-1]["ratio"]

    return None  # 구조 파악용 더미


async def _save_trend(
    keyword: str,
    topic_type: str,
    trend_date: date,
    score: float | None,
    source: str,
) -> None:
    """
    TRENDS 테이블에 저장.
    TOPIC + TREND_DATE + SOURCE 조합이 이미 있으면 upsert (중복 방지).
    실제 구현 시 SQLAlchemy AsyncSession 사용.
    """
    # TODO: DB 세션 열어서 INSERT OR UPDATE (upsert)
    pass
