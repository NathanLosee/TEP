"""Module for defining login request schema.

Classes:
    - Login: Pydantic schema for request/response data.

"""

from pydantic import BaseModel, ConfigDict


class Login(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        login_id (int): Unique identifier of the login.
        name (str): Name of the login.

    """

    id: int
    password: str

    model_config = ConfigDict(
        str_strip_whitespace=True, str_min_length=1, populate_by_name=True
    )
