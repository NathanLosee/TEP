"""Module for defining holiday request and response schemas.

Classes:
    - HolidayBase: Pydantic schema for request/response data.
    - HolidayGroupBase: Pydantic schema for request/response data.
    - HolidayGroupExtended: Base Pydantic schema extended with id field.

"""

from datetime import date
from typing import Optional

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
        is_recurring (bool): Whether the holiday recurs annually.
        recurrence_type (str): Type of recurrence - 'fixed' or 'relative'.
        recurrence_month (int): Month for recurrence (1-12).
        recurrence_day (int): Day of month for fixed recurrence (1-31).
        recurrence_week (int): Week of month for relative recurrence (1-5).
        recurrence_weekday (int): Day of week for relative recurrence (0-6).

    """

    name: str = Field(pattern=NAME_REGEX, max_length=NAME_MAX_LENGTH)
    start_date: date
    end_date: date
    is_recurring: bool = False
    recurrence_type: Optional[str] = None
    recurrence_month: Optional[int] = Field(None, ge=1, le=12)
    recurrence_day: Optional[int] = Field(None, ge=1, le=31)
    recurrence_week: Optional[int] = Field(None, ge=1, le=5)
    recurrence_weekday: Optional[int] = Field(None, ge=0, le=6)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_min_length=1,
        json_schema_extra={
            "example": {
                "name": "Christmas Day",
                "start_date": "2025-12-25",
                "end_date": "2025-12-25",
                "is_recurring": True,
                "recurrence_type": "fixed",
                "recurrence_month": 12,
                "recurrence_day": 25,
            }
        },
    )

    @model_validator(mode="after")
    def check_values(self):
        validate(
            self.start_date <= self.end_date,
            EXC_MSG_END_DATE_BEFORE_START_DATE,
            status.HTTP_400_BAD_REQUEST,
        )

        # Validate recurring holiday fields
        if self.is_recurring:
            validate(
                self.recurrence_type in ["fixed", "relative"],
                "Recurrence type must be 'fixed' or 'relative'",
                status.HTTP_400_BAD_REQUEST,
            )
            validate(
                self.recurrence_month is not None,
                "Recurrence month is required for recurring holidays",
                status.HTTP_400_BAD_REQUEST,
            )

            if self.recurrence_type == "fixed":
                validate(
                    self.recurrence_day is not None,
                    "Recurrence day is required for fixed recurring holidays",
                    status.HTTP_400_BAD_REQUEST,
                )
            elif self.recurrence_type == "relative":
                validate(
                    self.recurrence_week is not None,
                    "Recurrence week is required for "
                    "relative recurring holidays",
                    status.HTTP_400_BAD_REQUEST,
                )
                validate(
                    self.recurrence_weekday is not None,
                    "Recurrence weekday is required "
                    "for relative recurring holidays",
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

    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_min_length=1,
        json_schema_extra={
            "example": {
                "name": "US Federal Holidays",
                "holidays": [
                    {
                        "name": "New Year's Day",
                        "start_date": "2025-01-01",
                        "end_date": "2025-01-01",
                        "is_recurring": True,
                        "recurrence_type": "fixed",
                        "recurrence_month": 1,
                        "recurrence_day": 1,
                    },
                    {
                        "name": "Thanksgiving",
                        "start_date": "2025-11-27",
                        "end_date": "2025-11-27",
                        "is_recurring": True,
                        "recurrence_type": "relative",
                        "recurrence_month": 11,
                        "recurrence_week": 4,
                        "recurrence_weekday": 3,
                    },
                ],
            }
        },
    )

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
