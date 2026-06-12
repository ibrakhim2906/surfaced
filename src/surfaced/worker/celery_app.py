from celery import Celery
from celery.schedules import crontab

from surfaced.core.config import settings

celery_app = Celery(
    "surfaced.worker.celery",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["surfaced.worker.tasks"],
)

celery_app.conf.beat_schedule = {
    "scrape_and_load_hh_vacancies": {
        "task": "scrape_and_load_hh_vacancies",
        "schedule": crontab(hour=0, minute=0),
    },
    "enrich_hh_vacancies": {"task": "enrich_hh_vacancies", "schedule": 1800},
}
