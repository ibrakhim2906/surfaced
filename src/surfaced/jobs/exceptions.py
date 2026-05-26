from fastapi import HTTPException, status


def JobNotFoundException(job_id: int | None) -> HTTPException:  # noqa

    if job_id:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job listing with ID {job_id} could not be found",
        )

    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="The requested job vacancy could not be found or is no longer active.",
    )


def JobAlreadySavedException(job_id: int | None) -> HTTPException:  # noqa

    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Job with id {job_id} was already saved",
    )


def SavedJobNotFoundException(job_id: int | None):  # noqa

    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Job with id {job_id} is not found in your saved list",
    )
