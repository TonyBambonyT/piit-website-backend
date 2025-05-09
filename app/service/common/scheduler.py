from apscheduler.schedulers.background import BackgroundScheduler
from app.dao.db_config import SessionLocal
from app.service.common.data_sync_manager import DataSyncManager


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    _add_sync_job(scheduler)
    return scheduler


def _add_sync_job(scheduler: BackgroundScheduler):
    def job():
        db = SessionLocal()
        try:
            DataSyncManager(db).sync_all()
        finally:
            db.close()

    scheduler.add_job(
        job,
        trigger="cron",
        day_of_week="sun",
        hour=0,
        minute=0,
        id="weekly_sync"
    )
