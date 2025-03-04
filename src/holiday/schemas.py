"""Module for defining holiday request and response schemas.

Classes:
    - HolidayBase: Pydantic schema for request/response data.
    - HolidayExtended: Base Pydantic schema extended with id field.

"""

from datetime import date
from typing import Self
from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.holiday.constants import NAME_MAX_LENGTH, NAME_REGEX


class HolidayBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        name (str): Name of the holiday.
        start_date (date): Date of the start of the holiday.
        end_date (date): Date of the end of the holiday.
        org_unit_id (int): Identifier of the org unit associated with the
            holiday.

    """

    name: str = Field(pattern=NAME_REGEX, max_length=NAME_MAX_LENGTH)
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    org_unit_id: int = Field(alias="orgUnitId")

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    @model_validator(mode="after")
    def check_values(self) -> Self:
        if self.end_date < self.start_date:
            raise ValueError("endDate must be greater than startDate.")
        return self


class HolidayExtended(HolidayBase):
    """Base Pydantic schema extended with id field.

    Attributes:
        id (int): Unique identifier of the holiday's data in the database.

    """

    id: int

    model_config = ConfigDict(from_attributes=True)
