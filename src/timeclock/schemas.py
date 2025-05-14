"""Module for defining timeclock request and response schemas.

Classes:
    - TimeclockEntryBase: Pydantic schema for request/response data.

"""

from datetime import datetime
from fastapi import HTTPException, status
from pydantic import BaseModel, Field, model_validator
from src.timeclock.constants import EXC_MSG_CLOCK_OUT_BEFORE_CLOCK_IN


class TimeclockEntryBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        id (int): Unique identifier of the timeclock entry in the database.
        employee_id (int): The employee associated with this timeclock entry.
        clock_in (datetime): Timestamp of when the employee clocked in.
        clock_out (datetime | None): Timestamp of when the employee clocked
            out.

    """

    id: int
    employee_id: int
    clock_in: datetime
    clock_out: datetime | None = Field(default=None)

    @model_validator(mode="after")
    def check_datetimes(self):
        if self.clock_out and self.clock_out < self.clock_in:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=EXC_MSG_CLOCK_OUT_BEFORE_CLOCK_IN,
            )
        return self
