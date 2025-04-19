"""Module for defining org unit request and response schemas.

Classes:
    - OrgUnitBase: Pydantic schema for request/response data.
    - OrgUnitExtended: Base Pydantic schema extended with id field.

"""

from pydantic import BaseModel, ConfigDict, Field
from src.org_unit.constants import NAME_MAX_LENGTH, NAME_REGEX
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.employee.schemas import EmployeeBase
else:
    EmployeeBase = "EmployeeBase"


class OrgUnitBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        name (str): Name of the org unit.

    """

    name: str = Field(pattern=NAME_REGEX, max_length=NAME_MAX_LENGTH)

    model_config = ConfigDict(
        str_strip_whitespace=True, str_min_length=1, populate_by_name=True
    )


class OrgUnitExtended(OrgUnitBase):
    """Base Pydantic schema extended with id field.

    Attributes:
        id (int): Unique identifier of the org unit's data in the database.
        employees (list[EmployeeBase]): List of employees in the org unit.

    """

    id: int
    employees: list[EmployeeBase]

    model_config = ConfigDict(from_attributes=True)
