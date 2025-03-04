"""Module for defining holiday data models.

Classes:
    - Holiday: SQLAlchemy model for the 'holidays' table in the database.

"""

from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.holiday.constants import IDENTIFIER
from src.org_unit.models import OrgUnit


class Holiday(Base):
    """SQLAlchemy model for holiday data.

    Attributes:
        id (int): Unique identifier of the holiday's data in the database.
        name (str): Name of the holiday.
        date_of (date): Date of the holiday.
        org_unit_id (int): Identifier of the org unit associated with the
            holiday.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)
    org_unit_id: Mapped[int] = mapped_column(
        ForeignKey=OrgUnit.id, nullable=False
    )
    org_unit: Mapped[OrgUnit] = relationship(passive_deletes=True)

    __tablename__ = IDENTIFIER
