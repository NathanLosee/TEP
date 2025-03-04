"""Module for defining job request and response schemas.

Classes:
    - JobBase: Pydantic schema for request/response data.
    - JobExtended: Base Pydantic schema extended with id field.

"""

from pydantic import BaseModel, ConfigDict, Field
from src.job.constants import NAME_MAX_LENGTH, NAME_REGEX


class JobBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        job_id (int): Unique identifier of the job.
        name (str): Name of the job.
        department_id (int): Unique identifier of the department.

    """

    job_id: int
    name: str = Field(pattern=NAME_REGEX, max_length=NAME_MAX_LENGTH)
    department_id: int

    model_config = ConfigDict(
        str_strip_whitespace=True, str_min_length=1, populate_by_name=True
    )


class JobExtended(JobBase):
    """Base Pydantic schema extended with id field.

    Attributes:
        id (int): Unique identifier of the job's data in the database.

    """

    id: int

    model_config = ConfigDict(from_attributes=True)
