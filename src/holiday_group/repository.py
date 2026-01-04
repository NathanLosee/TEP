"""Module providing database interactivity for holiday-related operations."""

from typing import Union

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.holiday_group.models import Holiday, HolidayGroup
from src.holiday_group.schemas import HolidayGroupBase, HolidayGroupExtended


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
    holiday_group = HolidayGroup(
        **request.model_dump(exclude={"holidays"}),
        holidays=[Holiday(**h.model_dump()) for h in request.holidays],
    )
    db.add(holiday_group)
    db.commit()
    db.refresh(holiday_group)
    return holiday_group


def get_holiday_groups(db: Session) -> list[HolidayGroup]:
    """Retrieve all existing holiday groups.

    Args:
        db (Session): Database session for the current request.

    Returns:
        list[HolidayGroup]: The retrieved holiday groups.

    """
    return db.scalars(select(HolidayGroup)).all()


def get_holiday_group_by_id(id: int, db: Session) -> Union[HolidayGroup, None]:
    """Retrieve a holiday group by a provided id.

    Args:
        id (int): Holiday group's unique identifier.
        db (Session): Database session for the current request.

    Returns:
        (Union[HolidayGroup, None]): The holiday group with the provided id,
            or None if not found.

    """
    return db.get(HolidayGroup, id)


def get_holiday_group_by_name(
    name: str, db: Session
) -> Union[HolidayGroup, None]:
    """Retrieve a holiday group by a provided name.

    Args:
        name (str): Holiday group's name.
        db (Session): Database session for the current request.

    Returns:
        (Union[HolidayGroup, None]): The holiday group with the provided name,
            or None if not found.

    """
    return db.scalars(
        select(HolidayGroup).where(HolidayGroup.name == name)
    ).first()


def update_holiday_group_by_id(
    holiday_group: HolidayGroup,
    request: HolidayGroupExtended,
    db: Session,
) -> HolidayGroup:
    """Update a holiday group's existing data.

    Args:
        holiday_group (HolidayGroup): Holiday group data to be updated.
        request (HolidayGroupExtended): Request data for updating holiday
            group.
        db (Session): Database session for the current request.

    Returns:
        HolidayGroup: The updated holiday group.

    """
    holiday_group_update = HolidayGroup(
        **request.model_dump(exclude={"holidays"})
    )
    request_holidays = set(holiday.name for holiday in request.holidays)
    group_holidays = set(holiday.name for holiday in holiday_group.holidays)
    added_holidays = request_holidays - group_holidays
    removed_holidays = group_holidays - request_holidays
    updated_holidays = request_holidays & group_holidays
    for holiday in holiday_group.holidays:
        if holiday.name in removed_holidays:
            db.delete(holiday)
    for holiday in request.holidays:
        new_holiday = Holiday(**holiday.model_dump())
        if holiday.name in added_holidays:
            new_holiday.holiday_group_id = holiday_group_update.id
            db.add(new_holiday)
        elif holiday.name in updated_holidays:
            new_holiday.holiday_group_id = next(
                h for h in holiday_group.holidays if h.name == holiday.name
            ).holiday_group_id

    db.merge(holiday_group_update)
    db.commit()
    db.refresh(holiday_group)
    return holiday_group


def delete_holiday_group(holiday_group: HolidayGroup, db: Session) -> None:
    """Delete provided holiday group data.

    Args:
        holiday_group (HolidayGroup): Holiday group data to be delete.
        db (Session): Database session for the current request.

    """
    db.delete(holiday_group)
    db.commit()
