"""Module for defining holiday request and response schemas.

Classes:
    - HolidayBase: Pydantic schema for request/response data.
    - HolidayGroupBase: Pydantic schema for request/response data.
    - HolidayGroupExtended: Base Pydantic schema extended with id field.

"""

from datetime import date

from fastapi import status
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.holiday_group.constants import (
    EXC_MSG_DUPLICATE_HOLIDAY_NAME,
    EXC_MSG_END_DATE_BEFORE_START_DATE,
    NAME_MAX_LENGTH,
    NAME_REGEX,
)
from src.services import validate


class HolidayBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        name (str): Holiday's name.
        start_date (date): Holiday's start date.
        end_date (date): Holiday's end date.

    """

    name: str = Field(pattern=NAME_REGEX, max_length=NAME_MAX_LENGTH)
    start_date: date
    end_date: date

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    @model_validator(mode="after")
    def check_values(self):
        validate(
            self.start_date <= self.end_date,
            EXC_MSG_END_DATE_BEFORE_START_DATE,
            status.HTTP_400_BAD_REQUEST,
        )
        return self


class HolidayGroupBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        name (str): Holiday group's name.

    """

    name: str = Field(pattern=NAME_REGEX, max_length=NAME_MAX_LENGTH)
    holidays: list[HolidayBase]

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    @model_validator(mode="after")
    def check_values(self):
        holiday_names = [holiday.name for holiday in self.holidays]
        for holiday_name in set(holiday.name for holiday in self.holidays):
            validate(
                holiday_names.count(holiday_name) <= 1,
                EXC_MSG_DUPLICATE_HOLIDAY_NAME,
                status.HTTP_400_BAD_REQUEST,
            )
        return self


class HolidayGroupExtended(HolidayGroupBase):
    """Base Pydantic schema extended with id field.

    Attributes:
        id (int): Holiday group's unique identifier.

    """

    id: int

    model_config = ConfigDict(from_attributes=True)
