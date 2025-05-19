"""Module for defining user data models.

Classes:
    - Employee: SQLAlchemy model for the 'users' table in the database.

"""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.auth_role.constants import (
    MEMBERSHIP_IDENTIFIER as AUTH_ROLE_MEMBERSHIP_IDENTIFIER,
)
from src.database import Base
from src.employee.constants import IDENTIFIER as EMPLOYEE_IDENTIFIER
from src.user.constants import IDENTIFIER

if TYPE_CHECKING:
    from src.auth_role.models import AuthRole
else:
    AuthRole = "AuthRole"


class User(Base):
    """SQLAlchemy model for user data.

    Attributes:
        id (int): User's unique identifier.
        password (str): User's hashed password.

    """

    id: Mapped[int] = mapped_column(
        ForeignKey(EMPLOYEE_IDENTIFIER + ".id"),
        primary_key=True,
        nullable=False,
    )
    password: Mapped[str] = mapped_column(nullable=False)
    auth_roles: Mapped[list[AuthRole]] = relationship(
        secondary=AUTH_ROLE_MEMBERSHIP_IDENTIFIER,
        back_populates="users",
    )

    __tablename__ = IDENTIFIER


class InvalidatedToken(Base):
    """SQLAlchemy model for invalidated tokens.

    Attributes:
        token (str): The invalidated token.

    """

    token: Mapped[str] = mapped_column(primary_key=True, nullable=False)

    __tablename__ = "invalidated_tokens"
