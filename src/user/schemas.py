"""Module for defining user request schema.

Classes:
    - UserBase: Pydantic schema for user data.
    - UserResponse: Pydantic schema for user data.

"""

from pydantic import BaseModel


class UserBase(BaseModel):
    """Pydantic schema for user data.

    Attributes:
        id (int): User's unique identifier.
        password (str): User's password.

    """

    id: int
    password: str


class UserPasswordChange(UserBase):
    """Pydantic schema for user password change.

    Attributes:
        id (int): User's unique identifier.
        new_password (str): User's new password.

    """

    new_password: str


class UserResponse(BaseModel):
    """Pydantic schema for user data.

    Attributes:
        id (int): User's unique identifier.

    """

    id: int
