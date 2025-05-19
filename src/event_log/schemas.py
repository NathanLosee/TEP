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
        log (str): Event log's message.
        user_id (int): User's unique identifier.

    """

    log: str
    user_id: int

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)


class EventLogExtended(EventLogBase):
    """Pydantic schema for request/response data with id.

    Attributes:
        id (int): Event log's unique identifier.
        timestamp (datetime): Event log's timestamp when the event ocurred.

    """

    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
