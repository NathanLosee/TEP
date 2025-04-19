"""Module for defining department data models.

Classes:
    - Department: SQLAlchemy model for the 'departments' table in the database.
    - Department: SQLAlchemy model for the 'department_memberships' table in
        the database.

"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.department.constants import IDENTIFIER, MEMBERSHIP_IDENTIFIER
from src.employee.constants import IDENTIFIER as EMPLOYEE_IDENTIFIER
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.employee.models import Employee
else:
    Employee = "Employee"


class DepartmentMembership(Base):
    """SQLAlchemy model for DepartmentMembership data.

    Attributes:
        department_id (int): Unique identifier of the department in the
            membership.
        employee_id (int): Unique identifier of the employee in the membership.

    """

    department_id: Mapped[int] = mapped_column(
        ForeignKey(IDENTIFIER + ".id"), primary_key=True, nullable=False
    )
    employee_id: Mapped[int] = mapped_column(
        ForeignKey(EMPLOYEE_IDENTIFIER + ".id"),
        primary_key=True,
        nullable=False,
    )

    __tablename__ = MEMBERSHIP_IDENTIFIER


class Department(Base):
    """SQLAlchemy model for Department data.

    Attributes:
        id (int): Unique identifier of the departments's data in the database.
        name (str): Name of the department.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    employees: Mapped[list[Employee]] = relationship(
        secondary=DepartmentMembership,
        back_populates="departments",
        cascade="all, delete",
    )

    __tablename__ = IDENTIFIER
