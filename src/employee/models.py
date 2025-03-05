"""Module for defining employee data models.

Classes:
    - Employee: SQLAlchemy model for the 'employees' table in the database.

"""

from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.auth.models import AuthRole
from src.database import Base
from src.department.models import Department, DepartmentMembership
from src.employee.constants import IDENTIFIER
from src.org_unit.models import OrgUnit


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
        org_unit_id (int): Unique identifier of the org unit the employee
            belongs to.
        manager_id (int): Unique identifier of the employee's manager.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    alt_id: Mapped[int] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=True)
    payroll_type: Mapped[str] = mapped_column(nullable=False)
    payroll_sync: Mapped[date] = mapped_column(nullable=False)
    workweek_type: Mapped[str] = mapped_column(nullable=False)
    time_type: Mapped[bool] = mapped_column(nullable=False)
    allow_clocking: Mapped[bool] = mapped_column(nullable=False)
    allow_delete: Mapped[bool] = mapped_column(nullable=False)
    org_unit_id: Mapped[int] = mapped_column(nullable=False)
    manager_id: Mapped[int] = mapped_column(nullable=True)
    manager: Mapped["Employee"] = relationship("Employee")
    auth_roles: Mapped[AuthRole] = relationship(
        AuthRole, back_populates="employees"
    )
    org_unit: Mapped[OrgUnit] = relationship(
        OrgUnit, back_populates="employees"
    )
    departments: Mapped[list[Department]] = relationship(
        secondary=DepartmentMembership,
        back_populates="departments",
        cascade="all, delete",
    )
    manager: Mapped["Employee"] = relationship("Employee")

    __tablename__ = IDENTIFIER
