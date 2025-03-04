"""Module for defining department request and response schemas.

Classes:
    - DepartmentBase: Pydantic schema for request/response data.
    - DepartmentExtended: Base Pydantic schema extended with additional fields.

"""

from pydantic import BaseModel, ConfigDict, Field
from src.department.constants import NAME_MAX_LENGTH, NAME_REGEX
from src.employee.schemas import EmployeeExtended
from src.job.schemas import JobExtended


class DepartmentBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        department_id (int): Unique identifier of the department.
        name (str): Name of the department.

    """

    department_id: int
    name: str = Field(pattern=NAME_REGEX, max_length=NAME_MAX_LENGTH)

    model_config = ConfigDict(
        str_strip_whitespace=True, str_min_length=1, populate_by_name=True
    )


class DepartmentExtended(DepartmentBase):
    """Base Pydantic schema extended with id field.

    Attributes:
        id (int): Unique identifier of the department's data in the database.

    """

    id: int
    employees: list[EmployeeExtended]
    jobs: list[JobExtended]

    model_config = ConfigDict(from_attributes=True)
