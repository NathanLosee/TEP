"""Module for defining org unit data models.

Classes:
    - OrgUnit: SQLAlchemy model for the 'org_units' table in the database.

"""

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.org_unit.constants import IDENTIFIER

if TYPE_CHECKING:
    from src.employee.models import Employee
else:
    Employee = "Employee"


class OrgUnit(Base):
    """SQLAlchemy model for Org Unit data.

    Attributes:
        id (int): Org unit's unique identifier.
        name (str): Org unit's name.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    employees: Mapped[list[Employee]] = relationship(
        Employee, back_populates="org_unit", cascade="all, delete"
    )

    __tablename__ = IDENTIFIER
