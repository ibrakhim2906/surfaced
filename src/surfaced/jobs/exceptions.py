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
