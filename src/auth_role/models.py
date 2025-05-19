"""Module for defining auth role data models.

Classes:
    - AuthRole: SQLAlchemy model for the 'auth_roles' table in the database.
    - AuthRoleMembership: SQLAlchemy model for the 'auth_role_memberships'
        table in the database.
    - AuthRolePermission: SQLAlchemy model for the 'auth_role_permissions'
        table in the database.

"""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.auth_role.constants import (
    IDENTIFIER,
    MEMBERSHIP_IDENTIFIER,
    PERMISSION_IDENTIFIER,
)
from src.database import Base
from src.user.constants import IDENTIFIER as USER_IDENTIFIER

if TYPE_CHECKING:
    from src.user.models import User
else:
    User = "User"


class AuthRolePermission(Base):
    """SQLAlchemy model for AuthRolePermission data.

    Attributes:
        resource (str): Permission's resource name.
        auth_role_id (int): Auth role permission is associated with.

    """

    resource: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    auth_role_id: Mapped[int] = mapped_column(
        ForeignKey(IDENTIFIER + ".id"), primary_key=True, nullable=False
    )

    __tablename__ = PERMISSION_IDENTIFIER


class AuthRoleMembership(Base):
    """SQLAlchemy model for AuthRoleMembership data.

    Attributes:
        auth_role_id (int): Auth role in the membership.
        user_id (int): User in the membership.

    """

    auth_role_id: Mapped[int] = mapped_column(
        ForeignKey(IDENTIFIER + ".id"), primary_key=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(USER_IDENTIFIER + ".id"),
        primary_key=True,
        nullable=False,
    )

    __tablename__ = MEMBERSHIP_IDENTIFIER


class AuthRole(Base):
    """SQLAlchemy model for AuthRole data.

    Attributes:
        id (int): Auth role's unique identifier.
        name (str): Auth role's name.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    users: Mapped[list[User]] = relationship(
        secondary=MEMBERSHIP_IDENTIFIER,
        back_populates="auth_roles",
    )
    permissions: Mapped[list[AuthRolePermission]] = relationship(
        AuthRolePermission,
        cascade="all, delete",
    )

    __tablename__ = IDENTIFIER
