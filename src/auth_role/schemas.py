"""Module for defining auth role request and response schemas.

Classes:
    - PermissionBase: Pydantic schema for request/response data.
    - AuthRoleBase: Pydantic schema for request/response data.
    - AuthRoleExtended: Base Pydantic schema extended with additional fields.

"""

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.auth_role.constants import (
    EXC_MSG_INVALID_RESOURCE,
    NAME_MAX_LENGTH,
    NAME_REGEX,
)
from src.constants import RESOURCE_SCOPES


class PermissionBase(BaseModel):
    """Base Pydantic schema extended with id field.

    Attributes:
        resource (str): Permission's resource name.

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
        name (str): Auth role's name.
        permissions (list[PermissionBase]): List of permissions associated
            with this auth role.

    """

    name: str = Field(pattern=NAME_REGEX, max_length=NAME_MAX_LENGTH)
    permissions: list[PermissionBase]

    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_min_length=1,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "Manager",
                "permissions": [
                    {"resource": "employee.read"},
                    {"resource": "employee.create"},
                    {"resource": "timeclock.read"},
                ],
            }
        },
    )


class AuthRoleExtended(AuthRoleBase):
    """Base Pydantic schema extended with id field.

    Attributes:
        id (int): Auth role's unique identifier.

    """

    id: int

    model_config = ConfigDict(from_attributes=True)
