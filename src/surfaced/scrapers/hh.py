import asyncio

import httpx

from surfaced.core.config import settings
from surfaced.scrapers.hh_exceptions import HHFetchError

HH_VACANCIES_URL = "https://api.hh.ru/vacancies"

YOUR_EMAIL = settings.YOUR_EMAIL
USER_AGENT = f"surfaced/1.0 ({YOUR_EMAIL})"

ROLES_ID = ["96", "124", "114", "112", "160"]
PAGE_COUNT = 10


async def scrape_hh_vacancies():

    async with httpx.AsyncClient(timeout=10.0) as client:
        for page in range(PAGE_COUNT):
            params = {"per_page": 100, "page": str(page), "professional_role": ROLES_ID}

            try:
                response = await client.get(
                    HH_VACANCIES_URL,
                    headers={
                        "Authorization": f"Bearer {settings.HH_ACCESS_TOKEN}",
                        "User-Agent": USER_AGENT,
                    },
                    params=params,
                )

                if response.status_code == 200:
                    data = response.json()

                    items = data.get("items", [])

                    if not items:
                        break
                    pass

                    # TODO move to Celery

                elif response.status_code in (403, 401):
                    # TODO handle invalid token of hh api
                    pass

                else:
                    # TODO handle other exceptions
                    pass

                    await asyncio.sleep(2.0)

            except httpx.HTTPError as e:
                raise HHFetchError(page, e)

            await asyncio.sleep(1)
