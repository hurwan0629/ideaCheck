from app.collector.crawlers.news_crawler import crawl_news
from app.collector.crawlers.trends_crawler import crawl_trends
from app.collector.processors.market_processor import process_market_news
from app.collector.processors.policy_detector import detect_policy_changes
from app.collector.queue.reanalysis_queue import consume_reanalysis_queue

# 일반 함수 사용할 때 with ~ as ~ 문법을 통해 db 세션 받기
from app.db import get_session


def daily_job():
    # 순서 중요: 수집 → 저장/분류 → 감지 → 트렌드 → 재분석 큐 소비
    # 동기로 처리하기 때문에 await, gather() 등의 처리는 하지 않음

    with get_session() as db:
      # 뉴스들 모두 크롤링
      raw_news = crawl_news()

      # 크롤링된 데이터에서 뉴스, 정책 변경 등 확인
      process_market_news(db, raw_news)
      detect_policy_changes(db, raw_news)

    # api를 통해 트렌드 지수 가져오기
    crawl_trends()

    # 뉴스들 분석 완료 후 최근 정책이 자주 바뀐 뉴스들 올라오는 큐를 통해 경쟁사들 재분석
    consume_reanalysis_queue()
