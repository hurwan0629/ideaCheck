from app.collector.crawlers.competitor_crawler import crawl_competitors
from app.collector.processors.analysis_generator import generate_analyses_for_all
from app.db import get_session

def quarterly_job():
  with get_session() as db:
    crawl_competitors(db)
  with get_session() as db:
    generate_analyses_for_all(db)
