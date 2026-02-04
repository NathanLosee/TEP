"""Module providing database interactivity for event log-related operations."""

from datetime import datetime, timezone
from typing import Union

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.event_log.models import EventLog
from src.event_log.schemas import EventLogBase
from src.user.models import User


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


def get_event_log_by_id(id: int, db: Session) -> Union[EventLog, None]:
    """Retrieve event log entry by ID.

    Args:
        id (int): Event log's unique identifier.
        db (Session): Database session for the current request.

    Returns:
        Union[EventLog, None]: The retrieved event log or None if not found.

    """
    return db.get(EventLog, id)


def get_event_log_entries(
    start_timestamp: datetime,
    end_timestamp: datetime,
    badge_number: Union[str, None],
    log_filter: Union[str, None],
    db: Session,
) -> list[EventLog]:
    """Retrieve all event logs with given time period.
    If badge_number is provided, it will be used to filter the logs to
        those associated with the badge number.
    If log_filter is provided, it will be used to filter the logs to those
        containing the filter text.

    Args:
        start_timestamp (datetime): Start timestamp for the time period.
        end_timestamp (datetime): End timestamp for the time period.
        badge_number (str, optional): User's badge number.
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
    if badge_number is not None:
        query = query.where(EventLog.badge_number == badge_number)
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


def filter_logs_by_permissions(
    logs: list[EventLog], user: User, db: Session
) -> list[EventLog]:
    """Filter event logs based on user's permissions.

    Only returns logs for entities the user has read access to.

    Args:
        logs (list[EventLog]): The event logs to filter.
        user (User): The user whose permissions to check.
        db (Session): Database session for the current request.

    Returns:
        list[EventLog]: The filtered event logs.

    """
    # Build a set of permissions the user has
    user_permissions = set()
    for role in user.auth_roles:
        for permission in role.permissions:
            user_permissions.add(permission.resource)

    # Define which permissions allow viewing which types of logs
    permission_to_log_keywords = {
        'employee.read': ['employee', 'emp'],
        'department.read': ['department'],
        'org_unit.read': ['org unit'],
        'holiday_group.read': ['holiday'],
        'timeclock.read': ['timeclock', 'clock'],
        'user.read': ['user', 'auth', 'role', 'password'],
        'report.read': ['report'],
        'event_log.read': [],  # Already checked at route level
    }

    filtered_logs = []
    for log in logs:
        log_text_lower = log.log.lower()

        # Check if the log relates to an entity the user can read
        can_view = False
        for permission, keywords in permission_to_log_keywords.items():
            if permission in user_permissions:
                # If user has this permission, check if
                # log contains related keywords
                if not keywords:  # Empty list means always allow
                    can_view = True
                    break
                for keyword in keywords:
                    if keyword in log_text_lower:
                        can_view = True
                        break
            if can_view:
                break

        if can_view:
            filtered_logs.append(log)

    return filtered_logs
