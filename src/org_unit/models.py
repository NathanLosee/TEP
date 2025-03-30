"""Module for defining org unit data models.

Classes:
    - OrgUnit: SQLAlchemy model for the 'org_units' table in the database.

"""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.org_unit.constants import IDENTIFIER
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.employee.models import Employee
    from src.holiday.models import Holiday
else:
    Employee = "Employee"
    Holiday = "Holiday"


class OrgUnit(Base):
    """SQLAlchemy model for Org Unit data.

    Attributes:
        id (int): Unique identifier of the org units's data in the database.
        name (str): Name of the org unit.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    employees: Mapped[list[Employee]] = relationship(
        Employee, back_populates="org_unit", cascade="all, delete"
    )
    holidays: Mapped[list[Holiday]] = relationship(
        Holiday, back_populates="org_unit", cascade="all, delete"
    )

    __tablename__ = IDENTIFIER
