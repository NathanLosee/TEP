"""Module for defining user request schema.

Classes:
    - UserBase: Pydantic schema for user data.
    - UserResponse: Pydantic schema for user data.

"""

from pydantic import BaseModel


class UserBase(BaseModel):
    """Pydantic schema for user data.

    Attributes:
        badge_number (str): Employee's badge number.
        password (str): User's password.

    """

    badge_number: str
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
        badge_number (str): Employee's badge number.

    """

    id: int
    badge_number: str
