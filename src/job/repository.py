"""Module providing database interactivity for job-related operations.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.job.models import Job
from src.job.schemas import JobBase, JobExtended


def create_job(request: JobBase, db: Session) -> Job:
    """Insert new job data.

    Args:
        request (JobBase): Request data for new job.
        db (Session): Database session for the current request.

    Returns:
        Org_unit: The created job.

    """
    job = Job(**request.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_jobs(db: Session) -> list[Job]:
    """Retrieve all job data.

    Args:
        db (Session): Database session for the current request.

    Returns:
        list[Job]: The retrieved jobs.

    """
    return db.scalars(select(Job)).all()


def get_job_by_id(id: int, db: Session) -> Job | None:
    """Retrieve an job by a provided id.

    Args:
        id (int): The id of the job to look for.
        db (Session): Database session for the current request.

    Returns:
        (Job | None): The job with the provided id, or None if
            not found.

    """
    return db.get(Job, id)


def get_job_by_name_and_department(
    name: str, department_id: int, db: Session
) -> Job | None:
    """Retrieve an job by a provided name and department id.

    Args:
        name (str): The name of the job to look for.
        department_id (int): The id of the department to look for.
        db (Session): Database session for the current request.

    Returns:
        (Job | None): The job with the provided name and department id, or None
            if not found.

    """
    return db.scalars(
        select(Job)
        .where(Job.name == name)
        .where(Job.department_id == department_id)
    ).first()


def update_job(job: Job, request: JobExtended, db: Session) -> Job:
    """Update an job's existing data.

    Args:
        job (Job): The job data to be updated.
        request (JobExtended): Request data for updating job.
        db (Session): Database session for the current request.

    Returns:
        Job: The updated job.
    """
    job_update = Job(**request.model_dump())
    db.merge(job_update)
    db.commit()
    db.refresh(job)
    return job


def delete_job(job: Job, db: Session):
    """Delete an job's data.

    Args:
        job (Job): The job data to be deleted.
        db (Session): Database session for the current request.

    """
    db.delete(job)
    db.commit()
