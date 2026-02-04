"""Module for defining department request and response schemas.

Classes:
    - DepartmentBase: Pydantic schema for request/response data.
    - DepartmentExtended: Base Pydantic schema extended with additional fields.

"""

from pydantic import BaseModel, ConfigDict, Field

from src.department.constants import NAME_MAX_LENGTH, NAME_REGEX


class DepartmentBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        name (str): Department's name.

    """

    name: str = Field(pattern=NAME_REGEX, max_length=NAME_MAX_LENGTH)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_min_length=1,
        populate_by_name=True,
        json_schema_extra={"example": {"name": "Engineering"}},
    )


class DepartmentExtended(DepartmentBase):
    """Base Pydantic schema extended with id field.

    Attributes:
        id (int): Department's unique identifier.

    """

    id: int

    model_config = ConfigDict(from_attributes=True)
