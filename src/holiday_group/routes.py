"""Module defining API for holiday-related operations."""

from fastapi import APIRouter, Security, status, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.login.services import requires_permission
import src.services as common_services
from src.holiday_group.constants import BASE_URL, IDENTIFIER
import src.holiday_group.repository as holiday_repository
import src.holiday_group.services as holiday_services
from src.holiday_group.schemas import HolidayGroupBase, HolidayGroupExtended
from src.employee.schemas import EmployeeExtended
from src.event_log.constants import EVENT_LOG_MSGS
import src.event_log.routes as event_log_routes
from src.event_log.schemas import EventLogBase

router = APIRouter(prefix=BASE_URL, tags=["holiday_group"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=HolidayGroupExtended,
)
def create_holiday_group(
    request: HolidayGroupBase,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["holiday_group.create"]
    ),
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

    holiday_group = holiday_repository.create_holiday_group(request, db)
    event_log_routes.create_event_log(
        EventLogBase(
            log=EVENT_LOG_MSGS[IDENTIFIER]["CREATE"].format(
                holiday_group_id=holiday_group.id
            ),
            employee_id=caller_id,
        ),
        db,
    )
    return holiday_group


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[HolidayGroupExtended],
)
def get_holiday_groups(
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["holiday_group.read"]
    ),
):
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
def get_holiday_group_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["holiday_group.read"]
    ),
):
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


@router.get(
    "/{id}/employees",
    status_code=status.HTTP_200_OK,
    response_model=list[EmployeeExtended],
)
def get_employees_by_holiday_group(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["holiday_group.read", "employee.read"]
    ),
):
    """Retrieve employees for holiday group with provided id.

    Args:
        id (int): The holiday group's unique identifier.
        db (Session): Database session for current request.

    Returns:
        list[EmployeeExtended]: The retrieved employees.

    """
    holiday_group = holiday_repository.get_holiday_group_by_id(id, db)
    holiday_services.validate_holiday_group_exists(holiday_group)

    return holiday_group.employees


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=HolidayGroupExtended,
)
def update_holiday_group_by_id(
    id: int,
    request: HolidayGroupExtended,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["holiday_group.update"]
    ),
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

    holiday_group = holiday_repository.update_holiday_group_by_id(
        holiday_group, request, db
    )
    event_log_routes.create_event_log(
        EventLogBase(
            log=EVENT_LOG_MSGS[IDENTIFIER]["UPDATE"].format(
                holiday_group_id=holiday_group.id
            ),
            employee_id=caller_id,
        ),
        db,
    )
    return holiday_group


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_holiday_group_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["holiday_group.delete"]
    ),
):
    """Delete holiday group data with provided id.

    Args:
        id (int): The holiday group's unique identifier.
        db (Session): Database session for current request.

    """
    holiday_group = holiday_repository.get_holiday_group_by_id(id, db)
    holiday_services.validate_holiday_group_exists(holiday_group)

    holiday_repository.delete_holiday_group(holiday_group, db)
    event_log_routes.create_event_log(
        EventLogBase(
            log=EVENT_LOG_MSGS[IDENTIFIER]["DELETE"].format(
                holiday_group_id=holiday_group.id
            ),
            employee_id=caller_id,
        ),
        db,
    )
