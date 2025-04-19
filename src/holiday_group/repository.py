"""Module providing database interactivity for holiday-related operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.holiday_group.models import Holiday, HolidayGroup
from src.holiday_group.schemas import (
    HolidayBase,
    HolidayGroupBase,
    HolidayGroupExtended,
)


def create_holiday_group(
    request: HolidayGroupBase, db: Session
) -> HolidayGroup:
    """Insert new holiday group data.

    Args:
        request (HolidayGroupBase): Request data for new holiday group.
        db (Session): Database session for the current request.

    Returns:
        HolidayGroup: The created holiday group.

    """
    holiday_group = HolidayGroup(**request.model_dump())
    db.add(holiday_group)
    db.commit()
    db.refresh(holiday_group)
    return holiday_group


def create_holiday(
    request: HolidayBase, holiday_group_id: int, db: Session
) -> HolidayGroup:
    """Insert new holiday data.

    Args:
        request (HolidayBase): Request data for new holiday.
        holiday_group_id (int): The id of the holiday group to which the
            holiday belongs.
        db (Session): Database session for the current request.

    Returns:
        HolidayGroup: The created holiday group with the new holiday.

    """
    holiday = Holiday(
        **request.model_dump(), holiday_group_id=holiday_group_id
    )
    db.add(holiday)
    db.commit()
    return get_holiday_group_by_id(holiday_group_id, db)


def get_holiday_groups(db: Session) -> list[HolidayGroup]:
    """Retrieve all existing holiday groups.

    Args:
        db (Session): Database session for the current request.

    Returns:
        list[HolidayGroup]: The retrieved holiday groups.

    """
    return db.scalars(select(HolidayGroup)).all()


def get_holiday_group_by_id(id: int, db: Session) -> HolidayGroup | None:
    """Retrieve a holiday group by a provided id.

    Args:
        id (int): The id of the holiday group to look for.
        db (Session): Database session for the current request.

    Returns:
        (HolidayGroup | None): The holiday group with the provided id, or None
            if not found.

    """
    return db.get(HolidayGroup, id)


def get_holiday_group_by_name(name: str, db: Session) -> HolidayGroup | None:
    """Retrieve a holiday group by a provided name.

    Args:
        name (str): The name of the holiday group to look for.
        db (Session): Database session for the current request.

    Returns:
        (HolidayGroup | None): The holiday group with the provided name, or
            None if not found.

    """
    return db.scalars(
        select(HolidayGroup).where(HolidayGroup.name == name)
    ).first()


def get_holiday_by_name_and_group(
    name: str, holiday_group_id: int, db: Session
) -> Holiday | None:
    """Retrieve a holiday by a provided name and group id.

    Args:
        name (str): The name of the holiday to look for.
        holiday_group_id (int): The id of the holiday group to look for.
        db (Session): Database session for the current request.

    Returns:
        (Holiday | None): The holiday with the provided name and group id, or
            None if not found.

    """
    return db.scalars(
        select(Holiday).where(
            Holiday.name == name, Holiday.holiday_group_id == holiday_group_id
        )
    ).first()


def update_holiday_group_by_id(
    holiday_group: HolidayGroup,
    request: HolidayGroupExtended,
    db: Session,
) -> HolidayGroup:
    """Update a holiday group's existing data.

    Args:
        holiday_group (HolidayGroup): The holiday group data to be updated.
        request (HolidayGroupExtended): Request data for updating holiday
            group.
        db (Session): Database session for the current request.

    Returns:
        HolidayGroup: The updated holiday group.

    """
    holiday_group_update = HolidayGroup(**request.model_dump())
    db.merge(holiday_group_update)
    db.commit()
    db.refresh(holiday_group)
    return holiday_group


def update_holiday_by_name_and_group(
    request: HolidayBase,
    holiday_group_id: int,
    db: Session,
) -> HolidayGroup:
    """Update a holiday's existing data.

    Args:
        request (HolidayBase): The holiday data to be updated.
        holiday_group_id (int): The id of the holiday group to which the
            holiday belongs.
        db (Session): Database session for the current request.

    Returns:
        HolidayGroup: The updated holiday group with the updated holiday.

    """
    holiday_update = Holiday(**request.model_dump())
    db.merge(holiday_update)
    db.commit()
    return get_holiday_group_by_id(holiday_group_id, db)


def delete_holiday_group(holiday_group: HolidayGroup, db: Session) -> None:
    """Delete provided holiday group data.

    Args:
        holiday_group (HolidayGroup): The holiday group data to be delete.
        db (Session): Database session for the current request.

    """
    db.delete(holiday_group)
    db.commit()


def delete_holiday_by_name_and_group(
    name: str, holiday_group_id: int, db: Session
) -> None:
    """Delete provided holiday data.

    Args:
        name (str): The name of the holiday to be deleted.
        holiday_group_id (int): The id of the holiday group to which the
            holiday belongs.
        db (Session): Database session for the current request.

    """
    db.delete(
        db.scalars(
            select(Holiday).where(
                Holiday.holiday_group_id == holiday_group_id,
                Holiday.name == name,
            )
        ).first()
    )
    db.commit()
