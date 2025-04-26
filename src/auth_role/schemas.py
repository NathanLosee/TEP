"""Module for defining auth role request and response schemas.

Classes:
    - PermissionBase: Pydantic schema for request/response data.
    - PermissionExtended: Base Pydantic schema extended with id field.
    - AuthRoleBase: Pydantic schema for request/response data.
    - AuthRoleExtended: Base Pydantic schema extended with additional fields.

"""

from pydantic import BaseModel, ConfigDict, Field
from src.auth_role.constants import NAME_MAX_LENGTH, NAME_REGEX


class PermissionBase(BaseModel):
    """Base Pydantic schema extended with id field.

    Attributes:
        resource (str): The resource of the permission.
        http_method (str): The HTTP method of the permission.
        restrict_to_self (bool): Whether the permission is restricted to the
            employee.

    """

    resource: str
    http_method: str
    restrict_to_self: bool = False

    model_config = ConfigDict(
        str_strip_whitespace=True, str_min_length=1, populate_by_name=True
    )


class AuthRoleBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        name (str): Name of the auth role.
        permissions (list[PermissionBase]): List of permissions associated
            with this auth role.

    """

    name: str = Field(pattern=NAME_REGEX, max_length=NAME_MAX_LENGTH)
    permissions: list[PermissionBase]

    model_config = ConfigDict(
        str_strip_whitespace=True, str_min_length=1, populate_by_name=True
    )


class AuthRoleExtended(AuthRoleBase):
    """Base Pydantic schema extended with id field.

    Attributes:
        id (int): Unique identifier of the auth's data in the database.

    """

    id: int

    model_config = ConfigDict(from_attributes=True)
