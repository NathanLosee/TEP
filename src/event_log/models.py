"""Module for defining event log data models.

Classes:
    - Event_log: SQLAlchemy model for the 'event_log' table in the database.

"""

from datetime import datetime, timezone

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.employee.constants import IDENTIFIER as EMPLOYEE_IDENTIFIER
from src.event_log.constants import IDENTIFIER


class EventLog(Base):
    """SQLAlchemy model for event log data.

    Attributes:
        id (int): Event log's unique identifier.
        log (str): Event log's message.
        timestamp (datetime): Event log's timestamp.
        user_id (int): User's unique identifier.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    log: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(EMPLOYEE_IDENTIFIER + ".id"), nullable=False
    )

    __tablename__ = IDENTIFIER
