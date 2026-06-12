import asyncio
import re
from html.parser import HTMLParser
from typing import Any

from httpx import AsyncClient, HTTPError
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from surfaced.core.config import settings
from surfaced.jobs.models import Job
from surfaced.jobs.schemas import HHScrapeVacancySchema
from surfaced.scrapers import hh
from surfaced.scrapers.hh_exceptions import HHFetchError
from surfaced.scrapers.tech_stack_constant import TECH_MAP

HH_VACANCIES_URL = "https://api.hh.kz/vacancies"
HH_TOKEN_URL = "https://api.hh.kz/token"

YOUR_EMAIL = settings.YOUR_EMAIL
USER_AGENT = f"surfaced/1.0 ({YOUR_EMAIL})"
HH_CLIENT_ID = settings.HH_CLIENT_ID
HH_CLIENT_SECRET = settings.HH_CLIENT_SECRET
HH_APPLICATION_TOKEN = settings.HH_APPLICATION_TOKEN

ROLES_ID = ["96", "124", "114", "112", "160"]
PAGE_COUNT = 10
PER_PAGE = 100


async def _get_hh_access_token(client: AsyncClient):

    try:
        response = await client.post(
            HH_TOKEN_URL,
            headers={"User-Agent": USER_AGENT},
            params={
                "grant_type": "client_credentials",
                "client_id": HH_CLIENT_ID,
                "client_secret": HH_CLIENT_SECRET,
            },
        )

        _ = response.raise_for_status()

        return response.json()["access_token"]

    except Exception as e:
        raise RuntimeError(f"failed to get hh auth token: {e}")


async def scrape_hh_vacancies() -> list[Any]:

    parsed_data = []

    async with AsyncClient(timeout=10) as client:
        headers = {
            "Authorization": f"Bearer {HH_APPLICATION_TOKEN}",
            "User-Agent": USER_AGENT,
        }

        for page in range(PAGE_COUNT):
            params = {
                "per_page": PER_PAGE,
                "page": str(page),
                "professional_role": ROLES_ID,
                "area": 160,
            }

            try:
                response = await client.get(
                    HH_VACANCIES_URL, headers=headers, params=params
                )

                response.raise_for_status()

                if response.status_code == 200:
                    try:
                        data = response.json()

                    except Exception as e:
                        raise HHFetchError(page, e)

                    items = data.get("items", [])

                    if not items:
                        break

                    for item in items:
                        try:
                            validated_item = HHScrapeVacancySchema.model_validate(item)

                            mapped_item = validated_item.to_db_dict()

                            parsed_data.append(mapped_item)

                        except Exception as e:
                            print(f"[HH] skipped vacancy id={item.get('id')}: {e}")
                            continue

                    if page >= (data.get("pages", 1) - 1):
                        break

            except HTTPError as e:
                print(
                    f"[HH] page {page} HTTP error: {e.response.status_code} — {e.response.text[:300]}"
                )
                continue

            await asyncio.sleep(1)

    return parsed_data


async def load_jobs(session: AsyncSession, jobs_data: list[Any]) -> int:

    if not jobs_data:
        return 0

    try:
        query = insert(Job).values(jobs_data)

        query = query.on_conflict_do_update(
            index_elements=[Job.source_url],
            set_={
                "title": query.excluded.title,
                "salary_min": query.excluded.salary_min,
                "salary_max": query.excluded.salary_max,
                "is_archived": query.excluded.is_archived,
            },
        )

        await session.execute(query)
        await session.commit()

        return len(jobs_data)

    except Exception as e:
        await session.rollback()

        raise e


class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, data):
        self.fed.append(data)

    def get_data(self):
        return " ".join(self.fed)


def _strip_tags(content: str):
    s = HTMLStripper()
    s.feed(content)
    return s.get_data()


def _get_stack(description: str, skills: list[str]):

    stack: set[str] = set()

    text = description.lower()

    for skill in skills:
        skill = skill.lower().strip()
        if skill in TECH_MAP:
            stack.add(TECH_MAP[skill])
        elif len(skill) < 25:
            stack.add(skill)

    for key, name in TECH_MAP.items():
        escape_key = re.escape(key)

        pattern = rf"(?:^|[^a-zA-Z0-9_\+#\.])({escape_key})(?:$|[^a-zA-Z0-9_\+#\.])"

        if re.search(pattern, text):
            stack.add(name)

    return list(stack)


async def enrich_vacancies(session: AsyncSession):

    query = (
        select(Job)
        .where(
            Job.description.like("%Полное описание будет загружено в ближайшее время%")
        )
        .limit(hh.PAGE_COUNT)
    )

    result = await session.execute(query)

    jobs = result.scalars().all()

    if not jobs:
        # All jobs are enriched
        return

    async with AsyncClient(timeout=10) as client:
        try:
            token = await _get_hh_access_token(client)
        except RuntimeError:
            # TODO log
            return

        headers = {"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT}

        for job in jobs:
            url = f"https://api.hh.kz/vacancies/{job.source_id}"

            try:
                response = await client.get(url, headers=headers)

                response.raise_for_status()

                data = response.json()

                description = data.get("description", "")
                job.description = _strip_tags(description)

                skills = [s["name"] for s in data.get("key_skills", [])]
                job.stack = _get_stack(job.description, skills)

            except Exception:
                continue

            await asyncio.sleep(1)

        await session.commit()
