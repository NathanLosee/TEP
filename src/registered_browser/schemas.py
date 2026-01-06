"""Module for defining registered browser request and response schemas.

Classes:
    - RegisteredBrowserBase: Pydantic schema for request/response data.
    - RegisteredBrowserExtended: Extended schema with id.

"""

from pydantic import BaseModel, ConfigDict


class RegisteredBrowserBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        browser_uuid (str): Browser's unique UUID.
        browser_name (str): Browser's friendly name.

    """

    browser_uuid: str
    browser_name: str

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)


class RegisteredBrowserExtended(RegisteredBrowserBase):
    """Extended pydantic schema with additional fields.

    Attributes:
        id (int): Browser's unique identifier.

    """

    id: int

    model_config = ConfigDict(from_attributes=True)
