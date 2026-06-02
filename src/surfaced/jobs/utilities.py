import base64
from typing import Any

from surfaced.jobs.schemas import JobFilters


def create_cache_key(filters: JobFilters) -> str:
    return (
        f"jobs:search:"
        f"q={filters.q or 'all'}"
        f"loc={filters.location or 'all'}"
        f"lim={filters.limit or 20}"
        f"cur={filters.cursor or 'none'}"
    )


def create_cache_payload(
    serialized_items, next_cursor: str | None, has_more: bool
) -> dict[str, Any | str | bool | None]:
    return {"items": serialized_items, "next_cursor": next_cursor, "has_more": has_more}


def next_cursor_b64_encode(last_seen_id: str):
    return base64.b64encode(last_seen_id.encode()).decode()


def next_cursor_b64_decode(cursor_bytes: bytes):
    return base64.b64decode(cursor_bytes).decode()
