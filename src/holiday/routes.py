"""Module defining API for holiday-related operations."""

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from src.database import get_db
import src.services as common_services
from src.holiday.constants import BASE_URL
import src.holiday.repository as holiday_repository
import src.holiday.services as holiday_services
from src.holiday.schemas import HolidayBase, HolidayExtended

router = APIRouter(prefix=BASE_URL, tags=["holiday"])


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=HolidayExtended
)
def create_holiday(request: HolidayBase, db: Session = Depends(get_db)):
    """Insert new holiday data.

    Args:
        request (HolidayBase): Request data for new holiday.
        db (Session): Database session for current request.

    Returns:
        HolidayExtended: Response containing newly created holiday data.

    """
    holiday_with_same_date = (
        holiday_repository.get_holiday_by_name_and_org_unit(
            request.name, request.org_unit_id
        )
    )
    holiday_services.validate_holiday_name_is_unique_within_org_unit(
        holiday_with_same_date, None
    )

    return holiday_repository.create_holiday(request, db)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[HolidayExtended],
)
def get_holidays(db: Session = Depends(get_db)):
    """Retrieve all holiday data.

    Args:
        db (Session): Database session for current request.

    Returns:
        list[HolidayExtended]: The retrieved holidays.

    """
    return holiday_repository.get_holidays(db)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=HolidayExtended,
)
def get_holiday_by_id(id: int, db: Session = Depends(get_db)):
    """Retrieve data for holiday with provided id.

    Args:
        id (int): The holiday's unique identifier.
        db (Session): Database session for current request.

    Returns:
        HolidayExtended: The retrieved holiday.

    """
    holiday = holiday_repository.get_holiday_by_id(id, db)
    holiday_services.validate_holiday_exists(holiday)

    return holiday


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=HolidayExtended,
)
def update_holiday_by_id(
    id: int, request: HolidayExtended, db: Session = Depends(get_db)
):
    """Update data for holiday with provided id.

    Args:
        id (int): The holiday's unique identifier.
        request (HolidayBase): Request data to update holiday.
        db (Session): Database session for current request.

    Returns:
        HolidayExtended: The updated holiday.

    """
    common_services.validate_ids_match(request.id, id)
    holiday = holiday_repository.get_holiday_by_id(id, db)
    holiday_services.validate_holiday_exists(holiday)

    holiday_with_same_date = (
        holiday_repository.get_holiday_by_name_and_org_unit(
            request.name, request.org_unit_id, db
        )
    )
    holiday_services.validate_holiday_name_is_unique_within_org_unit(
        holiday_with_same_date, id
    )

    return holiday_repository.update_holiday_by_id(holiday, request, db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holiday_by_id(id: int, db: Session = Depends(get_db)):
    """Delete holiday data with provided id.

    Args:
        id (int): The holiday's unique identifier.
        db (Session): Database session for current request.

    """
    holiday = holiday_repository.get_holiday_by_id(id, db)
    holiday_services.validate_holiday_exists(holiday)

    holiday_repository.delete_holiday(holiday, db)
