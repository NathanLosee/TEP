"""Module for defining auth role request and response schemas.

Classes:
    - PermissionBase: Pydantic schema for request/response data.
    - PermissionExtended: Base Pydantic schema extended with id field.
    - AuthRoleBase: Pydantic schema for request/response data.
    - AuthRoleExtended: Base Pydantic schema extended with additional fields.

"""

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.auth_role.constants import (
    NAME_MAX_LENGTH,
    NAME_REGEX,
    EXC_MSG_INVALID_RESOURCE,
)
from src.constants import RESOURCE_SCOPES


class PermissionBase(BaseModel):
    """Base Pydantic schema extended with id field.

    Attributes:
        resource (str): The resource of the permission.

    """

    resource: str

    model_config = ConfigDict(
        str_strip_whitespace=True, str_min_length=1, populate_by_name=True
    )

    @model_validator(mode="after")
    def check_values(self):
        if self.resource not in RESOURCE_SCOPES.keys():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=EXC_MSG_INVALID_RESOURCE,
            )
        return self


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
