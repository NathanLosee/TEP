"""Module providing database interactivity for holiday-related operations."""

from datetime import date
from sqlalchemy import extract, select
from sqlalchemy.orm import Session
from src.holiday.models import Holiday
from src.holiday.schemas import HolidayBase, HolidayExtended


def create_holiday(request: HolidayBase, db: Session) -> Holiday:
    """Insert new holiday data.

    Args:
        request (HolidayBase): Request data for new holiday.
        db (Session): Database session for the current request.

    Returns:
        Holiday: The created holiday.

    """
    holiday = Holiday(**request.model_dump())
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    return holiday


def get_holidays(db: Session) -> list[Holiday]:
    """Retrieve all existing holidays.

    Args:
        db (Session): Database session for the current request.

    Returns:
        list[Holiday]: The retrieved holidays.

    """
    return db.scalars(select(Holiday)).all()


def get_holidays_by_year(year: int, db: Session) -> list[Holiday]:
    """Retrieve all holidays for a given year.

    Args:
        year (int): The year to look for.
        db (Session): Database session for the current request.

    Returns:
        list[Holiday]: The retrieved holidays for the given year.

    """
    return db.scalars(
        select(Holiday).where(extract("YEAR", Holiday.start_date) == year)
    ).all()


def get_holidays_by_month(month: int, db: Session) -> list[Holiday]:
    """Retrieve all holidays for a given month.

    Args:
        month (int): The month to look for.
        db (Session): Database session for the current request.

    Returns:
        list[Holiday]: The retrieved holidays for the given month.

    """
    return db.scalars(
        select(Holiday).where(extract("MONTH", Holiday.start_date) == month)
    ).all()


def get_holidays_by_date(date_of: date, db: Session) -> Holiday | None:
    """Retrieve all holidays for a given date.

    Args:
        date (str): The date of the holiday to look for.
        db (Session): Database session for the current request.

    Returns:
        list[Holiday]: The retrieved holidays for the given date.

    """
    return db.scalars(
        select(Holiday)
        .where(Holiday.start_date <= date_of)
        .where(Holiday.end_date >= date_of)
    ).first()


def get_holiday_by_id(id: int, db: Session) -> Holiday | None:
    """Retrieve an holiday by a provided id.

    Args:
        id (int): The id of the holiday to look for.
        db (Session): Database session for the current request.

    Returns:
        (Holiday | None): The holiday with the provided id, or None if not
            found.

    """
    return db.get(Holiday, id)


def get_holiday_by_name_and_org_unit(
    name: str, org_unit_id: int, db: Session
) -> Holiday | None:
    """Retrieve an holiday by a provided name and org unit id.

    Args:
        name (str): The name of the holiday to look for.
        org_unit_id (int): The id of the org unit to look for.
        db (Session): Database session for the current request.

    Returns:
        (Holiday | None): The holiday with the provided name and org unit id,
            or None if not found.

    """
    return db.scalars(
        select(Holiday)
        .where(Holiday.name == name)
        .where(Holiday.org_unit_id == org_unit_id)
    ).first()


def get_holiday_by_name(name: str, db: Session) -> Holiday | None:
    """Retrieve a holiday by a provided name.

    Args:
        name (str): The name of the holiday to look for.
        db (Session): Database session for the current request.

    Returns:
        (Holiday | None): The holiday with the provided name, or None if not
            found.

    """
    return db.scalars(select(Holiday).where(Holiday.name == name)).first()


def update_holiday_by_id(
    holiday: Holiday, request: HolidayExtended, db: Session
) -> Holiday:
    """Update a holiday's existing data.

    Args:
        holiday (Holiday): The holiday data to be updated.
        request (HolidayExtended): Request data for updating holiday.
        db (Session): Database session for the current request.

    Returns:
        Holiday: The updated holiday.

    """
    holiday_update = Holiday(**request.model_dump())
    db.merge(holiday_update)
    db.commit()
    db.refresh(holiday)
    return holiday


def delete_holiday(holiday: Holiday, db: Session) -> None:
    """Delete provided holiday data.

    Args:
        holiday (Holiday): The holiday data to be delete.
        db (Session): Database session for the current request.

    """
    db.delete(holiday)
    db.commit()
