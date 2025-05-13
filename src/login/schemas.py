"""Module for defining login request schema.

Classes:
    - Login: Pydantic schema for request/response data.

"""

from pydantic import BaseModel


class Token(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        access_token (str): The access token for the user.
        token_type (str): The type of the token (e.g., "bearer").

    """

    access_token: str
    token_type: str
