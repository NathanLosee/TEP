"""Module for defining holiday data models.

Classes:
    - Holiday: SQLAlchemy model for the 'holidays' table in the database.
    - HolidayGroup: SQLAlchemy model for the 'holiday_groups' table in the
        database.

"""

from datetime import date
from typing import TYPE_CHECKING, Optional

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
        is_recurring (bool): Whether the holiday recurs annually.
        recurrence_type (str): Type of recurrence - 'fixed' or 'relative'.
            'fixed': Same date every year (e.g., December 25)
            'relative': Relative date (e.g., First Monday in September)
        recurrence_month (int): Month for recurrence (1-12).
        recurrence_day (int): Day of month for fixed recurrence (1-31).
        recurrence_week (int): Week of month for relative recurrence (1-5).
            1=First, 2=Second, 3=Third, 4=Fourth, 5=Last
        recurrence_weekday (int): Day of week for relative recurrence (0-6).
            0=Monday, 6=Sunday

    """

    name: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)
    holiday_group_id: Mapped[int] = mapped_column(
        ForeignKey(IDENTIFIER + ".id"), primary_key=True, nullable=False
    )
    is_recurring: Mapped[bool] = mapped_column(nullable=False, default=False)
    recurrence_type: Mapped[Optional[str]] = mapped_column(nullable=True)
    recurrence_month: Mapped[Optional[int]] = mapped_column(nullable=True)
    recurrence_day: Mapped[Optional[int]] = mapped_column(nullable=True)
    recurrence_week: Mapped[Optional[int]] = mapped_column(nullable=True)
    recurrence_weekday: Mapped[Optional[int]] = mapped_column(nullable=True)

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
