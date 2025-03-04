"""Module for defining auth request and response schemas.

Classes:
    - AuthRoleBase: Pydantic schema for request/response data.
    - AuthRoleExtended: Base Pydantic schema extended with additional fields.

"""

from pydantic import BaseModel, ConfigDict, Field
from src.auth.constants import NAME_MAX_LENGTH, NAME_REGEX
from src.employee.schemas import EmployeeExtended


class AuthRoleBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        auth_role_id (int): Unique identifier of the auth role.
        name (str): Name of the auth role.

    """

    auth_role_id: int
    name: str = Field(pattern=NAME_REGEX, max_length=NAME_MAX_LENGTH)

    model_config = ConfigDict(
        str_strip_whitespace=True, str_min_length=1, populate_by_name=True
    )


class AuthRoleExtended(AuthRoleBase):
    """Base Pydantic schema extended with id field.

    Attributes:
        id (int): Unique identifier of the auth's data in the database.
        employees (list[EmployeeExtended]): List of employees with this auth.

    """

    id: int
    employees: list[EmployeeExtended]

    model_config = ConfigDict(from_attributes=True)
