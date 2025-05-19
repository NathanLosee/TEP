"""Module providing database interactivity for event log-related operations."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.event_log.models import EventLog
from src.event_log.schemas import EventLogBase


def create_event_log(request: EventLogBase, db: Session) -> EventLog:
    """Insert new event log data.

    Args:
        request (EventLogBase): Request data for new event log.
        db (Session): Database session for the current request.

    Returns:
        EventLog: The created event log entry.

    """
    event_log_entry = EventLog(
        **request.model_dump(), timestamp=datetime.now(timezone.utc)
    )
    db.add(event_log_entry)
    db.commit()
    db.refresh(event_log_entry)
    return event_log_entry


def get_event_log_by_id(id: int, db: Session) -> EventLog | None:
    """Retrieve event log entry by ID.

    Args:
        id (int): Event log's unique identifier.
        db (Session): Database session for the current request.

    Returns:
        EventLog | None: The retrieved event log or None if not found.

    """
    return db.get(EventLog, id)


def get_event_log_entries(
    start_timestamp: datetime,
    end_timestamp: datetime,
    user_id: int | None,
    log_filter: str | None,
    db: Session,
) -> list[EventLog]:
    """Retrieve all event logs with given time period.
    If user_id is provided, it will be used to filter the logs to
        those associated with the id.
    If log_filter is provided, it will be used to filter the logs to those
        containing the filter text.

    Args:
        start_timestamp (datetime): Start timestamp for the time period.
        end_timestamp (datetime): End timestamp for the time period.
        user_id (int, optional): User's unique identifier.
            Defaults to None.
        log_filter (str, optional): Filter for log messages.
            Defaults to None.
        db (Session): Database session for the current request.

    Returns:
        list[EventLog]: The retrieved event logs.

    """
    query = (
        select(EventLog)
        .where(EventLog.timestamp >= start_timestamp)
        .where(EventLog.timestamp <= end_timestamp)
    )
    if user_id is not None:
        query = query.where(EventLog.user_id == user_id)
    if log_filter:
        query = query.where(EventLog.log.ilike(f"%{log_filter}%"))
    return db.scalars(query).all()


def delete_event_log_entry(event_log: EventLog, db: Session) -> None:
    """Delete event log.

    Args:
        event_log (EventLog): Event log data to be deleted.
        db (Session): Database session for the current request.

    """
    db.delete(event_log)
    db.commit()
