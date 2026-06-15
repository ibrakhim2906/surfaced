import re

from typing import Any

import structlog
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import Message

from surfaced.core.config import settings
from surfaced.jobs.models import Job
from surfaced.scrapers.tech_stack_constant import TECH_MAP

logger = structlog.get_logger(__name__)

MESSAGES_LIMIT = 100

_SALARY_RE = re.compile(
    r"(?:от|зп|salary|зарплата|оплата)[:\s]*"
    r"(\d[\d\s]{2,})"
    r"(?:\s*[-–—]\s*(\d[\d\s]{2,}))?"
    r"(?:\s*([$€₸]|usd|eur|kzt|тг|тенге|\$))?",
    re.IGNORECASE,
)

_CURRENCY_SYMBOLS: dict[str, str] = {
    "$": "USD", "usd": "USD",
    "€": "EUR", "eur": "EUR",
    "₸": "KZT", "kzt": "KZT", "тг": "KZT", "тенге": "KZT",
}

_LOCATION_KEYWORDS: dict[str, str] = {
    "алматы": "Алматы",
    "almaty": "Алматы",
    "астана": "Астана",
    "нур-султан": "Астана",
    "nur-sultan": "Астана",
    "шымкент": "Шымкент",
    "shymkent": "Шымкент",
    "remote": "Remote",
    "удалённо": "Remote",
    "удаленно": "Remote",
    "онлайн": "Remote",
}

_NOISE_RE = re.compile(r"[^\w\s\+#\.\-]")


def _extract_salary(text: str) -> tuple[int | None, int | None, str]:
    m = _SALARY_RE.search(text)
    if not m:
        return None, None, "KZT"
    try:
        low = int(re.sub(r"\s", "", m.group(1)))
        high = int(re.sub(r"\s", "", m.group(2))) if m.group(2) else None
        currency_raw = (m.group(3) or "").lower().strip()
        currency = _CURRENCY_SYMBOLS.get(currency_raw, "KZT")
        return low, high, currency
    except (ValueError, TypeError):
        return None, None, "KZT"


def _extract_location(text: str) -> str | None:
    lower = text.lower()
    for keyword, location in _LOCATION_KEYWORDS.items():
        if keyword in lower:
            return location
    return None


def _extract_stack(text: str) -> list[str]:
    stack: set[str] = set()
    lower = text.lower()
    for key, name in TECH_MAP.items():
        pattern = rf"(?:^|[^a-zA-Z0-9_\+#\.])({re.escape(key)})(?:$|[^a-zA-Z0-9_\+#\.])"
        if re.search(pattern, lower):
            stack.add(name)
    return list(stack)


def _extract_title(text: str) -> str:
    for line in text.splitlines():
        cleaned = line.strip().lstrip("#").strip()
        if cleaned:
            return cleaned[:200]
    return text[:100]


def _message_to_db_dict(msg: Message, channel: str) -> dict[str, Any] | None:
    text = msg.message
    if not text or len(text) < 30:
        return None

    salary_min, salary_max, salary_currency = _extract_salary(text)
    posted_at = msg.date.replace(tzinfo=None) if msg.date else None

    return {
        "source_id": f"tg_{channel}_{msg.id}",
        "title": _extract_title(text),
        "company": channel,
        "location": _extract_location(text),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": salary_currency,
        "description": text,
        "stack": _extract_stack(text),
        "source": "telegram",
        "source_url": f"https://t.me/{channel}/{msg.id}",
        "posted_at": posted_at,
        "is_archived": False,
    }


async def scrape_telegram_channels() -> list[dict[str, Any]]:
    if not settings.TELEGRAM_SESSION_STRING:
        logger.error("telegram_session_missing")
        return []

    results: list[dict[str, Any]] = []

    async with TelegramClient(
        StringSession(settings.TELEGRAM_SESSION_STRING),
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH,
    ) as client:
        for channel in settings.TELEGRAM_CHANNELS:
            try:
                messages = await client.get_messages(channel, limit=MESSAGES_LIMIT)
                for msg in messages:
                    if not isinstance(msg, Message):
                        continue
                    row = _message_to_db_dict(msg, channel)
                    if row:
                        results.append(row)
                logger.info("telegram_channel_scraped", channel=channel, count=len(messages))
            except Exception as e:
                logger.error("telegram_channel_error", channel=channel, error=str(e))

    return results


async def load_telegram_jobs(session: AsyncSession, jobs_data: list[dict[str, Any]]) -> int:
    if not jobs_data:
        return 0

    try:
        query = insert(Job).values(jobs_data)
        query = query.on_conflict_do_update(
            index_elements=[Job.source_url],
            set_={
                "title": query.excluded.title,
                "description": query.excluded.description,
                "stack": query.excluded.stack,
                "is_archived": query.excluded.is_archived,
            },
        )
        await session.execute(query)
        await session.commit()
        return len(jobs_data)
    except Exception as e:
        await session.rollback()
        raise e
