from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.collector.jobs.daily import daily_job
from app.collector.jobs.quarterly import quarterly_job
from datetime import datetime

scheduler = AsyncIOScheduler()


def setup_scheduler():
    # 매일 가져올 뉴스 -> market정보, trend, competitor_policy
    scheduler.add_job(
        daily_job,
        CronTrigger(hour=3, minute=0),
        id="daily_job",
        replace_existing=True,
        next_run_time=datetime.now()
    )
    # 분기별 가져올 정보 - 경쟁사의 정적 정보를 가져올 예정. ex) 기업이 제공하는 서비스, 업종 등
    scheduler.add_job(
        quarterly_job,
        CronTrigger(month="1,4,7,10", day=1, hour=4, minute=0),
        id="quarterly_job",
        replace_existing=True,
        next_run_time=datetime.now()
    )
