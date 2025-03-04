"""Module defining API for job-related operations."""

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from src.database import get_db
import src.services as common_services
from src.job.constants import BASE_URL
import src.job.repository as job_repository
import src.job.services as job_services
from src.job.schemas import JobBase, JobExtended

router = APIRouter(prefix=BASE_URL, tags=["job"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=JobExtended,
)
def create_job(request: JobBase, db: Session = Depends(get_db)):
    """Insert new job.

    Args:
        request (JobBase): Request data for new job.
        db (Session): Database session for current request.

    Returns:
        JobExtended: Response containing newly created job
            data.

    """
    job_with_same_name = job_repository.get_job_by_name_and_department(
        request.name, request.department_id, db
    )
    job_services.validate_job_name_is_unique_within_department(
        job_with_same_name, None
    )

    return job_repository.create_job(request, db)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[JobExtended],
)
def get_jobs(
    db: Session = Depends(get_db),
):
    """Retrieve all jobs.

    Args:
        db (Session): Database session for current request.

    Returns:
        list[JobExtended]: The retrieved jobs.

    """
    return job_repository.get_jobs(db)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=list[JobExtended],
)
def get_job(id: int, db: Session = Depends(get_db)):
    """Retrieve data for job with provided id.

    Args:
        id (int): The job's unique identifier.
        db (Session): Database session for current request.

    Returns:
        JobExtended: The retrieved job.

    """
    job = job_repository.get_job_by_id(id, db)
    job_services.validate_job_exists(job)

    return job


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=JobExtended,
)
def update_job(
    id: int,
    request: JobExtended,
    db: Session = Depends(get_db),
):
    """Update data for job with provided id.

    Args:
        id (int): The job's unique identifier.
        request (JobBase): Request data to update job.
        db (Session): Database session for current request.

    Returns:
        JobExtended: The updated job.

    """
    common_services.validate_ids_match(request.job_id, id)
    job = job_repository.get_job_by_id(id, db)
    job_services.validate_job_exists(job)
    job_with_same_name = job_repository.get_job_by_name_and_department(
        request.name, request.department_id, db
    )
    job_services.validate_job_name_is_unique_within_department(
        job_with_same_name, id
    )

    return job_repository.update_job(job, request, db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(id: int, db: Session = Depends(get_db)):
    """Delete job with provided id.

    Args:
        id (int): The job's unique identifier.
        db (Session): Database session for current request.

    """
    job = job_repository.get_job_by_id(id, db)
    job_services.validate_job_exists(job)
    job_services.validate_job_employees_list_is_empty(job)

    job_repository.delete_job(job, db)
