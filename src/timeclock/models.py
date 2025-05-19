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
        employee_id (int): Employee's unique identifier.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    clock_in: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now(timezone.utc)
    )
    clock_out: Mapped[datetime] = mapped_column(nullable=True, default=None)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey(EMPLOYEE_IDENTIFIER + ".id"), nullable=False
    )

    __tablename__ = IDENTIFIER
