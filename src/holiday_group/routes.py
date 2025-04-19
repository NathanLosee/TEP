"""Module defining API for holiday-related operations."""

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from src.database import get_db
import src.services as common_services
from src.holiday_group.constants import BASE_URL
import src.holiday_group.repository as holiday_repository
import src.holiday_group.services as holiday_services
from src.holiday_group.schemas import (
    HolidayBase,
    HolidayGroupBase,
    HolidayGroupExtended,
)

router = APIRouter(prefix=BASE_URL, tags=["holiday_group"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=HolidayGroupExtended,
)
def create_holiday_group(
    request: HolidayGroupBase, db: Session = Depends(get_db)
):
    """Insert new holiday group data.

    Args:
        request (HolidayGroupBase): Request data for new holiday group.
        db (Session): Database session for current request.

    Returns:
        HolidayGroupExtended: Response containing newly created holiday group
            data.

    """
    holiday_group_with_same_name = (
        holiday_repository.get_holiday_group_by_name(request.name, db)
    )
    holiday_services.validate_holiday_group_name_is_unique(
        holiday_group_with_same_name, None
    )

    return holiday_repository.create_holiday_group(request, db)


@router.post(
    "{id}/holidays",
    status_code=status.HTTP_201_CREATED,
    response_model=HolidayGroupExtended,
)
def create_holiday(
    id: int, request: HolidayBase, db: Session = Depends(get_db)
):
    """Insert new holiday data.

    Args:
        id (int): The holiday group's unique identifier.
        request (HolidayBase): Request data for new holiday.
        db (Session): Database session for current request.

    Returns:
        HolidayExtended: Response containing newly created holiday data.

    """
    holiday_services.validate_holiday_group_exists(
        holiday_repository.get_holiday_group_by_id(id, db)
    )

    holiday_with_same_date = holiday_repository.get_holiday_by_name_and_group(
        request.name, id
    )
    holiday_services.validate_holiday_name_is_unique_within_group(
        holiday_with_same_date, None
    )

    return holiday_repository.create_holiday(request, db)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[HolidayGroupExtended],
)
def get_holiday_groups(db: Session = Depends(get_db)):
    """Retrieve all holiday group data.

    Args:
        db (Session): Database session for current request.

    Returns:
        list[HolidayGroupExtended]: The retrieved holiday groups.

    """
    return holiday_repository.get_holiday_groups(db)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=HolidayGroupExtended,
)
def get_holiday_group_by_id(id: int, db: Session = Depends(get_db)):
    """Retrieve data for holiday group with provided id.

    Args:
        id (int): The holiday group's unique identifier.
        db (Session): Database session for current request.

    Returns:
        HolidayGroupExtended: The retrieved holiday group.

    """
    holiday_group = holiday_repository.get_holiday_group_by_id(id, db)
    holiday_services.validate_holiday_group_exists(holiday_group)

    return holiday_group


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=HolidayGroupExtended,
)
def update_holiday_group_by_id(
    id: int, request: HolidayGroupExtended, db: Session = Depends(get_db)
):
    """Update data for holiday group with provided id.

    Args:
        id (int): The holiday group's unique identifier.
        request (HolidayGroupBase): Request data to update holiday group.
        db (Session): Database session for current request.

    Returns:
        HolidayGroupExtended: The updated holiday group.

    """
    common_services.validate_ids_match(request.id, id)
    holiday_group = holiday_repository.get_holiday_group_by_id(id, db)
    holiday_services.validate_holiday_group_exists(holiday_group)

    holiday_group_with_same_name = (
        holiday_repository.get_holiday_group_by_name(request.name, db)
    )
    holiday_services.validate_holiday_group_name_is_unique(
        holiday_group_with_same_name, id
    )

    return holiday_repository.update_holiday_group_by_id(
        holiday_group, request, db
    )


@router.put(
    "/{id}/holidays",
    status_code=status.HTTP_200_OK,
    response_model=HolidayGroupExtended,
)
def update_holiday(
    id: int, request: HolidayBase, db: Session = Depends(get_db)
):
    """Update data for holiday with provided id.

    Args:
        id (int): The holiday group's unique identifier.
        request (HolidayBase): Request data to update holiday.
        db (Session): Database session for current request.

    Returns:
        HolidayGroupExtended: The updated holiday group.

    """
    holiday_services.validate_holiday_group_exists(
        holiday_repository.get_holiday_group_by_id(id, db)
    )
    holiday = holiday_repository.get_holiday_by_name_and_group(
        request.name, id, db
    )
    holiday_services.validate_holiday_exists(holiday)

    return holiday_repository.update_holiday_by_name_and_group(request, id, db)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_holiday_group_by_id(id: int, db: Session = Depends(get_db)):
    """Delete holiday group data with provided id.

    Args:
        id (int): The holiday group's unique identifier.
        db (Session): Database session for current request.

    """
    holiday_group = holiday_repository.get_holiday_group_by_id(id, db)
    holiday_services.validate_holiday_group_exists(holiday_group)

    holiday_repository.delete_holiday_group(holiday_group, db)


@router.delete("/{id}/holidays", status_code=status.HTTP_204_NO_CONTENT)
def delete_holiday(id: int, name: str, db: Session = Depends(get_db)):
    """Delete holiday data with provided id.

    Args:
        id (int): The holiday's unique identifier.
        name (str): The holiday's name.
        db (Session): Database session for current request.

    """
    holiday_services.validate_holiday_group_exists(
        holiday_repository.get_holiday_group_by_id(id, db)
    )

    holiday = holiday_repository.get_holiday_by_name_and_group(name, id, db)
    holiday_services.validate_holiday_exists(holiday)

    holiday_repository.delete_holiday_by_name_and_group(name, id, db)
