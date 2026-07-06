"""Scrape HeadHunter + Telegram and load into the database the env points to.

Run locally or from CI (GitHub Actions) to seed / refresh the production DB
without needing a persistent Celery worker.

    PYTHONPATH=src uv run python scripts/scrape.py
"""

import asyncio

from surfaced.core.database import async_session_factory
from surfaced.scrapers.hh import enrich_vacancies, load_jobs, scrape_hh_vacancies
from surfaced.scrapers.telegram import load_telegram_jobs, scrape_telegram_channels


async def main() -> None:
    print("Scraping HeadHunter...")
    hh_jobs = await scrape_hh_vacancies()
    print(f"  fetched {len(hh_jobs)} HH vacancies")
    if hh_jobs:
        async with async_session_factory() as session:
            loaded = await load_jobs(session, hh_jobs)
            print(f"  loaded {loaded} HH jobs")

    print("Enriching HeadHunter jobs (full descriptions + tech stack)...")
    async with async_session_factory() as session:
        await enrich_vacancies(session)

    print("Scraping Telegram...")
    tg_jobs = await scrape_telegram_channels()
    print(f"  fetched {len(tg_jobs)} Telegram messages")
    if tg_jobs:
        async with async_session_factory() as session:
            loaded = await load_telegram_jobs(session, tg_jobs)
            print(f"  loaded {loaded} Telegram jobs")

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
