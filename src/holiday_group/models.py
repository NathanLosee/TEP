"""Module for defining holiday data models.

Classes:
    - Holiday: SQLAlchemy model for the 'holidays' table in the database.
    - HolidayGroup: SQLAlchemy model for the 'holiday_groups' table in the
        database.

"""

from datetime import date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.holiday_group.constants import IDENTIFIER, HOLIDAY_IDENTIFIER
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.employee.models import Employee
else:
    Employee = "Employee"


class HolidayGroup(Base):
    """SQLAlchemy model for holiday group data.

    Attributes:
        id (int): Unique identifier of the holiday group in the database.
        name (str): Name of the holiday group.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    holidays: Mapped[list["Holiday"]] = relationship(
        IDENTIFIER, back_populates="holiday_group"
    )
    employees: Mapped[list[Employee]] = relationship(
        Employee, back_populates="holiday_group"
    )

    __tablename__ = IDENTIFIER


class Holiday(Base):
    """SQLAlchemy model for holiday data.

    Attributes:
        name (str): Name of the holiday.
        start_date (date): Start date of the holiday.
        end_date (date): End date of the holiday.
        holiday_group_id (int): Foreign key referencing the holiday group.

    """

    name: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)
    holiday_group_id: Mapped[int] = mapped_column(
        ForeignKey("holiday_groups.id"), primary_key=True, nullable=False
    )
    holiday_group: Mapped[HolidayGroup] = relationship(
        HolidayGroup, back_populates="holidays"
    )

    __tablename__ = HOLIDAY_IDENTIFIER
