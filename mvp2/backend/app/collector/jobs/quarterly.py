from app.collector.crawlers.competitor_crawler import crawl_competitors
from app.collector.processors.analysis_generator import generate_analyses_for_all


def quarterly_job():
    crawl_competitors()
    generate_analyses_for_all()
