from fastapi import HTTPException, status


def JobNotFoundException(job_id: int) -> HTTPException:  # noqa

    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Job listing with ID {job_id} could not be found",
    )
