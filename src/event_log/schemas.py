"""Module for defining event log request and response schemas.

Classes:
    - EventLogBase: Pydantic schema for request/response data.
    - EventLogExtended: Pydantic schema for request/response data with id.

"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class EventLogBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        log (str): Log message associated with the event.
        employee_id (int): ID of the employee associated with the event.

    """

    log: str
    employee_id: int

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)


class EventLogExtended(EventLogBase):
    """Pydantic schema for request/response data with id.

    Attributes:
        id (int): Unique identifier of the event log in the database.
        timestamp (datetime): Timestamp of when the event occurred.

    """

    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
