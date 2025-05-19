"""Module for defining org unit request and response schemas.

Classes:
    - OrgUnitBase: Pydantic schema for request/response data.
    - OrgUnitExtended: Base Pydantic schema extended with id field.

"""

from pydantic import BaseModel, ConfigDict, Field

from src.org_unit.constants import NAME_MAX_LENGTH, NAME_REGEX


class OrgUnitBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        name (str): Org unit's name.

    """

    name: str = Field(pattern=NAME_REGEX, max_length=NAME_MAX_LENGTH)

    model_config = ConfigDict(
        str_strip_whitespace=True, str_min_length=1, populate_by_name=True
    )


class OrgUnitExtended(OrgUnitBase):
    """Base Pydantic schema extended with id field.

    Attributes:
        id (int): Org unit's unique identifier.

    """

    id: int

    model_config = ConfigDict(from_attributes=True)
