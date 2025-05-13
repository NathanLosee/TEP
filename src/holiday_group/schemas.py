"""Module for defining holiday request and response schemas.

Classes:
    - HolidayBase: Pydantic schema for request/response data.
    - HolidayGroupBase: Pydantic schema for request/response data.
    - HolidayGroupExtended: Base Pydantic schema extended with id field.

"""

from datetime import date
from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.holiday_group.constants import (
    NAME_MAX_LENGTH,
    NAME_REGEX,
    EXC_MSG_END_DATE_BEFORE_START_DATE,
    EXC_MSG_DUPLICATE_HOLIDAY_NAME,
)


class HolidayBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        name (str): Name of the holiday.
        start_date (date): Date of the start of the holiday.
        end_date (date): Date of the end of the holiday.

    """

    name: str = Field(pattern=NAME_REGEX, max_length=NAME_MAX_LENGTH)
    start_date: date
    end_date: date

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    @model_validator(mode="after")
    def check_values(self):
        if self.end_date < self.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=EXC_MSG_END_DATE_BEFORE_START_DATE,
            )
        return self


class HolidayGroupBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        name (str): Name of the holiday group.

    """

    name: str = Field(pattern=NAME_REGEX, max_length=NAME_MAX_LENGTH)
    holidays: list[HolidayBase]

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    @model_validator(mode="after")
    def check_values(self):
        holiday_names = [holiday.name for holiday in self.holidays]
        for holiday_name in set(holiday.name for holiday in self.holidays):
            if holiday_names.count(holiday_name) > 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=EXC_MSG_DUPLICATE_HOLIDAY_NAME,
                )
        return self


class HolidayGroupExtended(HolidayGroupBase):
    """Base Pydantic schema extended with id field.

    Attributes:
        id (int): Unique identifier of the holiday group's data in the
            database.

    """

    id: int

    model_config = ConfigDict(from_attributes=True)
