"""Module providing database interactivity for timeclock-related operations."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.employee.models import Employee
from src.timeclock.models import TimeclockEntry
from src.timeclock.schemas import TimeclockEntryBase, TimeclockEntryWithName


def timeclock(badge_number: str, db: Session) -> bool:
    """Clock in/out an employee.

    Args:
        badge_number (str): Employee's badge number.
        db (Session): Database session for the current request.

    Returns:
        bool: True if clocked in, False if clocked out.

    """
    timeclock = db.scalars(
        select(TimeclockEntry)
        .where(TimeclockEntry.badge_number == badge_number)
        .order_by(TimeclockEntry.id.desc())
    ).first()
    if timeclock and not timeclock.clock_out:
        timeclock.clock_out = datetime.now(timezone.utc)
        db.commit()
        return False
    else:
        new_timeclock = TimeclockEntry(badge_number=badge_number)
        db.add(new_timeclock)
        db.commit()
        return True


def check_status(
    badge_number: str,
    db: Session,
) -> bool:
    """Check if an employee is clocked in.

    Args:
        badge_number (str): Employee's badge number.
        db (Session): Database session for the current request.

    Returns:
        bool: True if clocked in, False if clocked out.

    """
    timeclock = db.scalars(
        select(TimeclockEntry)
        .where(TimeclockEntry.badge_number == badge_number)
        .order_by(TimeclockEntry.id.desc())
    ).first()
    return timeclock is not None and not timeclock.clock_out


def get_timeclock_entries(
    start_timestamp: datetime,
    end_timestamp: datetime,
    badge_number: str | None,
    first_name: str | None,
    last_name: str | None,
    db: Session,
) -> list[TimeclockEntryWithName]:
    """Retrieve all timeclocks with given time period.

    Args:
        start_timestamp (datetime): Start timestamp for the time period.
        end_timestamp (datetime): End timestamp for the time period.
        badge_number (str | None): Employee's badge number.
            Defaults to None.
        first_name (str | None): Employee's first name to filter by.
            Defaults to None.
        last_name (str | None): Employee's last name to filter by.
            Defaults to None.
        db (Session): Database session for the current request.

    Returns:
        list[TimeclockEntryWithName]: The retrieved timeclock entries with
            employee names.

    """
    query = select(
        TimeclockEntry, Employee.first_name, Employee.last_name
    ).join(Employee)
    query = query.where(
        TimeclockEntry.clock_in >= start_timestamp,
        TimeclockEntry.clock_in <= end_timestamp,
    )
    if badge_number:
        query = query.where(
            TimeclockEntry.badge_number.contains(f"{badge_number}")
        )
    if first_name:
        query = query.where(Employee.first_name.contains(f"{first_name}"))
    if last_name:
        query = query.where(Employee.last_name.contains(f"{last_name}"))
    results = db.execute(query).all()
    return [
        TimeclockEntryWithName(
            **row._tuple()[0].__dict__,
            first_name=row._tuple()[1],
            last_name=row._tuple()[2],
        )
        for row in results
    ]


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
    timeclock_entry.clock_in = request.clock_in
    timeclock_entry.clock_out = request.clock_out
    timeclock_entry.badge_number = request.badge_number
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
