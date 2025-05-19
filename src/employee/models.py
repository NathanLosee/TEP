"""Module for defining employee data models.

Classes:
    - Employee: SQLAlchemy model for the 'employees' table in the database.

"""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.department.constants import (
    MEMBERSHIP_IDENTIFIER as DEPARTMENT_MEMBERSHIP_IDENTIFIER,
)
from src.employee.constants import IDENTIFIER
from src.holiday_group.constants import IDENTIFIER as HOLIDAY_GROUP_IDENTIFIER
from src.org_unit.constants import IDENTIFIER as ORG_UNIT_IDENTIFIER

if TYPE_CHECKING:
    from src.department.models import Department
    from src.holiday_group.models import HolidayGroup
    from src.org_unit.models import OrgUnit
else:
    Department = "Department"
    HolidayGroup = "HolidayGroup"
    OrgUnit = "OrgUnit"


class Employee(Base):
    """SQLAlchemy model for employee data.

    Attributes:
        id (int): Employee's unique identifier.
        first_name (str): Employee's first name.
        last_name (str): Employee's last name.
        payroll_type (str): Employee's payroll type.
        payroll_sync (date): Employee's payroll sync date.
        workweek_type (str): Employee's workweek type.
        time_type (bool): Employee's time type.
            (True for full-time, False for part-time)
        allow_clocking (bool): Whether the employee is allowed to clock in/out.
        allow_delete (bool): Whether the employee is allowed to be deleted.
        org_unit_id (int): Org unit's unique identifier.
        manager_id (int): Manager's unique identifier.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    payroll_type: Mapped[str] = mapped_column(nullable=False)
    payroll_sync: Mapped[date] = mapped_column(nullable=False)
    workweek_type: Mapped[str] = mapped_column(nullable=False)
    time_type: Mapped[bool] = mapped_column(nullable=False)
    allow_clocking: Mapped[bool] = mapped_column(nullable=False)
    allow_delete: Mapped[bool] = mapped_column(nullable=False)
    holiday_group_id: Mapped[int] = mapped_column(
        ForeignKey(HOLIDAY_GROUP_IDENTIFIER + ".id"),
        nullable=True,
    )
    org_unit_id: Mapped[int] = mapped_column(
        ForeignKey(ORG_UNIT_IDENTIFIER + ".id"),
        nullable=False,
    )
    manager_id: Mapped[int] = mapped_column(
        ForeignKey(IDENTIFIER + ".id"),
        nullable=True,
    )
    manager: Mapped["Employee"] = relationship(
        "Employee", lazy="joined", join_depth=1
    )
    holiday_group: Mapped[HolidayGroup] = relationship(
        HolidayGroup,
        back_populates="employees",
    )
    org_unit: Mapped[OrgUnit] = relationship(
        OrgUnit,
        back_populates="employees",
    )
    departments: Mapped[list[Department]] = relationship(
        secondary=DEPARTMENT_MEMBERSHIP_IDENTIFIER,
        back_populates="employees",
    )

    __tablename__ = IDENTIFIER
