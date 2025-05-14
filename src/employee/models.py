"""Module for defining employee data models.

Classes:
    - Employee: SQLAlchemy model for the 'employees' table in the database.

"""

from datetime import date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.department.constants import (
    MEMBERSHIP_IDENTIFIER as DEPARTMENT_MEMBERSHIP_IDENTIFIER,
)
from src.employee.constants import IDENTIFIER
from src.org_unit.constants import IDENTIFIER as ORG_UNIT_IDENTIFIER
from src.auth_role.constants import (
    MEMBERSHIP_IDENTIFIER as AUTH_ROLE_MEMBERSHIP_IDENTIFIER,
)
from src.holiday_group.constants import IDENTIFIER as HOLIDAY_GROUP_IDENTIFIER
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.auth_role.models import AuthRole
    from src.department.models import Department
    from src.holiday_group.models import HolidayGroup
    from src.org_unit.models import OrgUnit
else:
    AuthRole = "AuthRole"
    Department = "Department"
    HolidayGroup = "HolidayGroup"
    OrgUnit = "OrgUnit"


class Employee(Base):
    """SQLAlchemy model for employee data.

    Attributes:
        id (int): Unique identifier of the employee's data in the database.
        alt_id (int): Alternate identifier of the employee's data in the
            database.
        first_name (str): First name of the employee.
        last_name (str): Last name of the employee.
        password (str): Password of the employee.
        payroll_type (str): Payroll type of the employee.
        payroll_sync (date): Date of the payroll time sync for the employee.
        workweek_type (str): Workweek type of the employee.
        time_type (bool): Whether the employee is full-time or part-time.
        allow_clocking (bool): Whether the employee is allowed to clock in/out.
        allow_delete (bool): Whether the employee is allowed to be deleted.
        auth_role_id (int): Unique identifier of the auth role the employee
            possesses.
        org_unit_id (int): Unique identifier of the org unit the employee
            belongs to.
        manager_id (int): Unique identifier of the employee's manager.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    alt_id: Mapped[int] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=True)
    payroll_type: Mapped[str] = mapped_column(nullable=False)
    payroll_sync: Mapped[date] = mapped_column(nullable=False)
    workweek_type: Mapped[str] = mapped_column(nullable=False)
    time_type: Mapped[bool] = mapped_column(nullable=False)
    allow_clocking: Mapped[bool] = mapped_column(nullable=False)
    allow_delete: Mapped[bool] = mapped_column(nullable=False)
    holiday_group_id: Mapped[int] = mapped_column(
        ForeignKey(HOLIDAY_GROUP_IDENTIFIER + ".id"), nullable=True
    )
    org_unit_id: Mapped[int] = mapped_column(
        ForeignKey(ORG_UNIT_IDENTIFIER + ".id"), nullable=False
    )
    manager_id: Mapped[int] = mapped_column(
        ForeignKey(IDENTIFIER + ".id"), nullable=True
    )
    manager: Mapped["Employee"] = relationship("Employee")
    org_unit: Mapped[OrgUnit] = relationship(
        OrgUnit, back_populates="employees"
    )
    auth_roles: Mapped[list[AuthRole]] = relationship(
        secondary=AUTH_ROLE_MEMBERSHIP_IDENTIFIER,
        back_populates="employees",
        cascade="all, delete",
    )
    departments: Mapped[list[Department]] = relationship(
        secondary=DEPARTMENT_MEMBERSHIP_IDENTIFIER,
        back_populates="employees",
        cascade="all, delete",
    )
    holiday_group: Mapped[HolidayGroup] = relationship(
        HolidayGroup, back_populates="employees"
    )

    __tablename__ = IDENTIFIER
