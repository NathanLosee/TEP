"""Module for defining timeclock data models.

Classes:
    - Timeclock: SQLAlchemy model for the 'timeclock' table in the database.

"""

from datetime import datetime, timezone

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.employee.constants import IDENTIFIER as EMPLOYEE_IDENTIFIER
from src.timeclock.constants import IDENTIFIER


class TimeclockEntry(Base):
    """SQLAlchemy model for timeclock data.

    Attributes:
        id (int): Timeclock entry's unique identifier.
        clock_in (datetime): Employee's clock-in timestamp.
        clock_out (datetime): Employee's clock-out timestamp.
        badge_number (str): Employee's badge number.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    clock_in: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now(timezone.utc), index=True
    )
    clock_out: Mapped[datetime] = mapped_column(nullable=True, default=None)
    badge_number: Mapped[str] = mapped_column(
        ForeignKey(EMPLOYEE_IDENTIFIER + ".badge_number", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    __tablename__ = IDENTIFIER
