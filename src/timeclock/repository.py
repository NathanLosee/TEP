"""Module providing database interactivity for timeclock-related operations."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.timeclock.models import TimeclockEntry
from src.timeclock.schemas import TimeclockEntryBase


def timeclock(employee_id: int, db: Session) -> bool:
    """Clock in/out an employee.

    Args:
        employee_id (int): Employee's unique identifier.
        db (Session): Database session for the current request.

    Returns:
        bool: True if clocked in, False if clocked out.

    """
    timeclock = db.scalars(
        select(TimeclockEntry)
        .where(TimeclockEntry.employee_id == employee_id)
        .order_by(TimeclockEntry.id.desc())
    ).first()
    if timeclock and not timeclock.clock_out:
        timeclock.clock_out = datetime.now(timezone.utc)
        db.commit()
        return False
    else:
        new_timeclock = TimeclockEntry(employee_id=employee_id)
        db.add(new_timeclock)
        db.commit()
        return True


def check_status(
    employee_id: int,
    db: Session,
) -> bool:
    """Check if an employee is clocked in.

    Args:
        employee_id (int): Employee's unique identifier.
        db (Session): Database session for the current request.

    Returns:
        bool: True if clocked in, False if clocked out.

    """
    timeclock = db.scalars(
        select(TimeclockEntry)
        .where(TimeclockEntry.employee_id == employee_id)
        .order_by(TimeclockEntry.id.desc())
    ).first()
    return timeclock is not None and not timeclock.clock_out


def get_timeclock_entries(
    start_timestamp: datetime,
    end_timestamp: datetime,
    employee_id: int | None,
    db: Session,
) -> list[TimeclockEntry]:
    """Retrieve all timeclocks with given time period.
    If employee_id is provided, it will be used to filter the logs to
        those associated with the id.

    Args:
        start_timestamp (datetime): Start timestamp for the time period.
        end_timestamp (datetime): End timestamp for the time period.
        employee_id (int | None): Employee's unique identifier.
            Defaults to None.
        db (Session): Database session for the current request.

    Returns:
        list[TimeclockEntry]: The retrieved timeclock entries.

    """
    query = select(TimeclockEntry).where(
        TimeclockEntry.clock_in >= start_timestamp,
        TimeclockEntry.clock_in <= end_timestamp,
    )
    if employee_id:
        query = query.where(TimeclockEntry.employee_id == employee_id)
    return db.scalars(query).all()


def get_timeclock_entry_by_id(id: int, db: Session) -> TimeclockEntry | None:
    """Retrieve timeclock entry by ID.

    Args:
        id (int): Timeclock entry's unique identifier.
        db (Session): Database session for the current request.

    Returns:
        TimeclockEntry | None: The retrieved timeclock entry or None if not
            found.

    """
    return db.get(TimeclockEntry, id)


def update_timeclock_entry_by_id(
    timeclock_entry: TimeclockEntry,
    request: TimeclockEntryBase,
    db: Session,
) -> TimeclockEntry:
    """Update a timeclock entry's existing data.

    Args:
        timeclock_entry (TimeclockEntry): Timeclock data to be updated.
        request (TimeclockEntryBase): Request data for updating timeclock
            entry.
        db (Session): Database session for the current request.

    Returns:
        TimeclockEntry: The updated timeclock entry.

    """
    timeclock_entry.employee_id = request.employee_id
    timeclock_entry.clock_in = request.clock_in
    timeclock_entry.clock_out = request.clock_out
    db.commit()
    return timeclock_entry


def delete_timeclock_entry(
    timeclock_entry: TimeclockEntry, db: Session
) -> None:
    """Delete timeclock entry.

    Args:
        timeclock_entry (TimeclockEntry): Timeclock data to be deleted.
        db (Session): Database session for the current request.

    """
    db.delete(timeclock_entry)
    db.commit()
