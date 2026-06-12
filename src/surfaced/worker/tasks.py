import asyncio

from surfaced.core.database import async_session_factory
from surfaced.scrapers.hh import enrich_vacancies, load_jobs, scrape_hh_vacancies
from surfaced.worker.celery_app import celery_app


@celery_app.task(name="scrape_and_load_hh_vacancies", bind=True, max_retries=3)
def task_scrape_and_load_hh_vacancies(self) -> int | None:

    async def scrape_pipeline():
        try:
            jobs_data = await scrape_hh_vacancies()

        except Exception as e:
            return e, None

        print(f"--- DEBUG: HeadHunter API returned {len(jobs_data)} total items ---")

        if not jobs_data:
            return None, 0

        async with async_session_factory() as session:
            result = await load_jobs(session, jobs_data)

            print(f"--- DEBUG: Database session loaded {result} items ---")
            return None, result

    error, result = asyncio.run(scrape_pipeline())

    if error is not None:
        raise self.retry(exc=error, countdown=60)

    return result


@celery_app.task(name="enrich_hh_vacancies", bind=False)
def task_enrich_hh_vacancies():

    async def process_enrich():
        async with async_session_factory() as session:
            await enrich_vacancies(session)

    asyncio.run(process_enrich())
