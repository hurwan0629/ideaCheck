from app.collector.crawlers.competitor_crawler import crawl_competitors
from app.collector.processors.analysis_generator import generate_analyses_for_all
from app.db import get_session

def quarterly_job():
  with get_session() as db:
    print("crawl_competitors 시작")
    crawl_competitors(db)
  with get_session() as db:
    print("generate_analyses_for_all (경쟁사 분석) 시작")
    generate_analyses_for_all(db)
    print("generate_analyses_for_all (경쟁사 분석) 종료")
