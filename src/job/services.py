"""Module providing the business logic for job-related operations."""

from typing import Optional
from fastapi import HTTPException, status
from src.job.constants import (
    EXC_MSG_JOB_NOT_FOUND,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_EMPLOYEES_ASSIGNED,
)
from src.job.models import Job


def validate_job_exists(job: Job | None) -> bool:
    """Return whether the provided job exists.

    Args:
        job (Job): The job to validate.

    Raises:
        HTTPException (404): If job does not exist.

    Returns:
        bool: True if job exists.

    """
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXC_MSG_JOB_NOT_FOUND,
        )
    return True


def validate_job_name_is_unique_within_department(
    job_with_same_name: Job, update_job_id: Optional[int]
) -> bool:
    """Return whether the provided job name is unique within a department.

    Args:
        job_with_same_name (Job): The job that has the
            same name and department provided in the request.
        update_job_id (Optional[int]): Unique identifier of the
            job being updated. Allows job to keep same name.

    Raises:
        HTTPException (409): If the provided name is already in use.

    Returns:
        bool: True if job name is unique.

    """
    if (
        job_with_same_name is not None
        and job_with_same_name.id != update_job_id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=EXC_MSG_NAME_ALREADY_EXISTS,
        )
    return True


def validate_job_employees_list_is_empty(
    job: Job | None,
) -> bool:
    """Return whether the provided job has employees.

    Args:
        job (Job): The job to validate.

    Raises:
        HTTPException (409): If job does have employees.

    Returns:
        bool: True if job does not have employees.

    """
    if job.employees is not None and len(job.employees) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=EXC_MSG_EMPLOYEES_ASSIGNED,
        )
    return True
