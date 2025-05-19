"""Module for defining holiday data models.

Classes:
    - Holiday: SQLAlchemy model for the 'holidays' table in the database.
    - HolidayGroup: SQLAlchemy model for the 'holiday_groups' table in the
        database.

"""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.holiday_group.constants import HOLIDAY_IDENTIFIER, IDENTIFIER

if TYPE_CHECKING:
    from src.employee.models import Employee
else:
    Employee = "Employee"


class Holiday(Base):
    """SQLAlchemy model for holiday data.

    Attributes:
        name (str): Holiday's name.
        start_date (date): Holiday's start date.
        end_date (date): Holiday's end date.
        holiday_group_id (int): Holiday group the holiday belongs to.

    """

    name: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)
    holiday_group_id: Mapped[int] = mapped_column(
        ForeignKey(IDENTIFIER + ".id"), primary_key=True, nullable=False
    )

    __tablename__ = HOLIDAY_IDENTIFIER


class HolidayGroup(Base):
    """SQLAlchemy model for holiday group data.

    Attributes:
        id (int): Holiday group's unique identifier.
        name (str): Holiday group's name.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    holidays: Mapped[list["Holiday"]] = relationship(
        Holiday, cascade="all, delete"
    )
    employees: Mapped[list[Employee]] = relationship(
        Employee, back_populates="holiday_group"
    )

    __tablename__ = IDENTIFIER
