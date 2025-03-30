"""Module for defining auth role data models.

Classes:
    - AuthRole: SQLAlchemy model for the 'auth_roles' table in the database.
    - AuthRoleMembership: SQLAlchemy model for the 'auth_role_memberships'
        table in the database.
    - AuthRolePermission: SQLAlchemy model for the 'auth_role_permissions'
        table in the database.

"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.auth_role.constants import (
    IDENTIFIER,
    MEMBERSHIP_IDENTIFIER,
    PERMISSION_IDENTIFIER,
)
from src.employee.constants import IDENTIFIER as EMPLOYEE_IDENTIFIER
from src.constants import HTTPMethod, ResourceType
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.employee.models import Employee
else:
    Employee = "Employee"


class AuthRolePermission(Base):
    """SQLAlchemy model for AuthRolePermission data.

    Attributes:
        auth_role_id (int): Unique identifier of the auth role in the
            membership.
        http_method (str): The HTTP method of the permission.
        resource (str): The resource of the permission.
        restrict_to_self (bool): Whether the permission is restricted to the
            employee.

    """

    auth_role_id: Mapped[int] = mapped_column(
        ForeignKey(IDENTIFIER + ".id"), primary_key=True, nullable=False
    )
    http_method: Mapped[HTTPMethod] = mapped_column(
        primary_key=True, nullable=False
    )
    resource: Mapped[ResourceType] = mapped_column(
        primary_key=True, nullable=False
    )
    restrict_to_self: Mapped[bool] = mapped_column(nullable=False)

    __tablename__ = PERMISSION_IDENTIFIER


class AuthRoleMembership(Base):
    """SQLAlchemy model for AuthRoleMembership data.

    Attributes:
        auth_role_id (int): Unique identifier of the auth role in the
            membership.
        employee_id (int): Unique identifier of the employee in the membership.

    """

    auth_role_id: Mapped[int] = mapped_column(
        ForeignKey(IDENTIFIER + ".id"), primary_key=True, nullable=False
    )
    employee_id: Mapped[int] = mapped_column(
        ForeignKey(EMPLOYEE_IDENTIFIER + ".id"),
        primary_key=True,
        nullable=False,
    )

    __tablename__ = MEMBERSHIP_IDENTIFIER


class AuthRole(Base):
    """SQLAlchemy model for AuthRole data.

    Attributes:
        id (int): Unique identifier of the auth role's data in the database.
        name (str): Name of the auth role.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    employees: Mapped[list["Employee"]] = relationship(
        secondary=MEMBERSHIP_IDENTIFIER,
        back_populates="auth_roles",
        cascade="all, delete",
    )
    permissions: Mapped[list[AuthRolePermission]] = relationship(
        MEMBERSHIP_IDENTIFIER,
        cascade="all, delete",
    )

    __tablename__ = IDENTIFIER
