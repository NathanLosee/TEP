"""Module for defining timeclock request and response schemas.

Classes:
    - TimeclockEntryBase: Pydantic schema for request/response data.

"""

from datetime import datetime

from fastapi import status
from pydantic import BaseModel, Field, model_validator

from src.services import validate
from src.timeclock.constants import EXC_MSG_CLOCK_OUT_BEFORE_CLOCK_IN


class TimeclockPunchRequest(BaseModel):
    """Optional request body for clock in/out punches.

    When provided, client_timestamp is used instead of server time.
    This supports offline punch sync where the original punch time
    must be preserved.

    Attributes:
        client_timestamp (datetime | None): Original
            punch timestamp from client.

    """

    client_timestamp: datetime | None = Field(default=None)


class TimeclockEntryCreate(BaseModel):
    """Pydantic schema for creating a new timeclock entry.

    Attributes:
        badge_number (str): Employee's badge number.
        clock_in (datetime): Employee's clock-in timestamp.
        clock_out (datetime | None): Employee's clock-out timestamp.

    """

    badge_number: str
    clock_in: datetime
    clock_out: datetime | None = Field(default=None)

    model_config = {
        "json_schema_extra": {
            "example": {
                "badge_number": "EMP001",
                "clock_in": "2025-01-15T08:00:00",
                "clock_out": "2025-01-15T17:00:00",
            }
        }
    }

    @model_validator(mode="after")
    def check_datetimes(self):
        validate(
            not self.clock_out or self.clock_out >= self.clock_in,
            EXC_MSG_CLOCK_OUT_BEFORE_CLOCK_IN,
            status.HTTP_400_BAD_REQUEST,
        )
        return self


class TimeclockEntryBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        id (int): Timeclock entry's unique identifier.
        badge_number (str): Employee's badge number.
        clock_in (datetime): Employee's clock-in timestamp.
        clock_out (datetime | None): Employee's clock-out timestamp.

    """

    id: int
    badge_number: str
    clock_in: datetime
    clock_out: datetime | None = Field(default=None)

    @model_validator(mode="after")
    def check_datetimes(self):
        validate(
            not self.clock_out or self.clock_out >= self.clock_in,
            EXC_MSG_CLOCK_OUT_BEFORE_CLOCK_IN,
            status.HTTP_400_BAD_REQUEST,
        )
        return self


class TimeclockEntryWithName(TimeclockEntryBase):
    """Pydantic schema for request/response data with employee names.

    Attributes:
        first_name (str): Employee's first name.
        last_name (str): Employee's last name.

    """

    first_name: str
    last_name: str
