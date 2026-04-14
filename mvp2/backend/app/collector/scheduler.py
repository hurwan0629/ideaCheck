# APScheduler: 특정 시간 간격 또는 특정 시각에 함수를 자동으로 실행시키는 라이브러리
# AsyncIOScheduler: FastAPI가 async 기반이라 async와 호환되는 스케줄러 사용
# 공식문서: https://apscheduler.readthedocs.io/en/3.x/
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger        # 특정 시각 반복 (매일 오전 3시 등)
from apscheduler.triggers.interval import IntervalTrigger # 일정 간격 반복 (N시간마다 등)

from app.collector.crawlers.news_crawler import crawl_news
from app.collector.crawlers.trends_crawler import crawl_trends
from app.collector.crawlers.competitor_crawler import crawl_competitors
from app.collector.processors.market_processor import process_market_news
from app.collector.processors.policy_detector import detect_policy_changes
from app.collector.processors.analysis_generator import generate_analyses_for_all
from app.collector.queue.reanalysis_queue import consume_reanalysis_queue

# 스케줄러 인스턴스 — 앱 전체에서 하나만 존재
scheduler = AsyncIOScheduler()


def setup_scheduler():
    """
    FastAPI startup 이벤트에서 호출.
    어떤 함수를 언제 실행할지 등록만 하고 start()로 가동.
    """

    # ── 매일 오전 3시 실행 (daily_job) ──────────────────────────────────────
    # CronTrigger: cron 문법으로 실행 시각 지정
    # hour=3, minute=0 → 매일 03:00
    scheduler.add_job(
        daily_job,
        CronTrigger(hour=3, minute=0),
        id="daily_job",
        replace_existing=True,  # 앱 재시작 시 중복 등록 방지
    )

    # ── 분기 1회 (quarterly_job) ─────────────────────────────────────────────
    # 매월 1일 오전 4시에 실행하되, month="1,4,7,10" → 1/4/7/10월만 실행 = 분기 1회
    scheduler.add_job(
        quarterly_job,
        CronTrigger(month="1,4,7,10", day=1, hour=4, minute=0),
        id="quarterly_job",
        replace_existing=True,
    )


async def daily_job():
    """
    매일 실행되는 수집 파이프라인.
    순서가 중요함: 수집 → 저장 → 분석 → 큐 소비
    """
    # 1. 뉴스 크롤링 (원본만 가져옴, 저장은 다음 단계에서)
    raw_news = await crawl_news()

    # 2. 뉴스를 DB에 저장하고 AI로 MARKET_EXTRACTS 생성
    await process_market_news(raw_news)

    # 3. 뉴스에서 경쟁사 정책 변경 감지 → COMPETITOR_POLICIES 저장
    #    변경이 많은 경쟁사는 재분석 큐에 자동 적재
    await detect_policy_changes(raw_news)

    # 4. Google Trends / 네이버 DataLab API 호출 → TRENDS 저장
    await crawl_trends()

    # 5. 재분석 큐에 쌓인 경쟁사 즉시 재분석
    await consume_reanalysis_queue()


async def quarterly_job():
    """
    분기 1회 실행: 경쟁사 공식 사이트 전체 재크롤링 + AI 종합 분석
    """
    # 1. 경쟁사 공식 사이트 크롤링 → COMPETITORS, COMPETITOR_FEATURES 갱신
    await crawl_competitors()

    # 2. 전 경쟁사 AI 종합 분석 → COMPETITOR_ANALYSES 새 행 + 임베딩 벡터 저장
    await generate_analyses_for_all()
