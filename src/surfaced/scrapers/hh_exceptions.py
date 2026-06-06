import httpx
from fastapi import HTTPException, status


def HHFetchError(page_number: int, e: httpx.HTTPError):  # noqa

    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Network Error fetching {page_number}: {e}",
    )
