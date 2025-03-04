"""Module defining API for org unit-related operations."""

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.employee.schemas import EmployeeExtended
from src.holiday.schemas import HolidayExtended
import src.services as common_services
from src.org_unit.constants import BASE_URL
import src.org_unit.repository as org_unit_repository
import src.org_unit.services as org_unit_services
from src.org_unit.schemas import OrgUnitBase, OrgUnitExtended

router = APIRouter(prefix=BASE_URL, tags=["org_unit"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=OrgUnitExtended,
)
def create_org_unit(request: OrgUnitBase, db: Session = Depends(get_db)):
    """Insert new org unit.

    Args:
        request (OrgUnitBase): Request data for new org unit.
        db (Session): Database session for current request.

    Returns:
        OrgUnitExtended: Response containing newly created org unit data.

    """
    org_unit_with_same_name = org_unit_repository.get_org_unit_by_name(
        request.name, db
    )
    org_unit_services.validate_org_unit_name_is_unique(
        org_unit_with_same_name, None
    )

    return org_unit_repository.create_org_unit(request, db)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[OrgUnitExtended],
)
def get_org_units(db: Session = Depends(get_db)):
    """Retrieve all org units.

    Args:
        db (Session): Database session for current request.

    Returns:
        list[OrgUnitExtended]: The retrieved org units.

    """
    return org_unit_repository.get_org_units(db)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=list[OrgUnitExtended],
)
def get_org_unit(id: int, db: Session = Depends(get_db)):
    """Retrieve data for org unit with provided id.

    Args:
        id (int): The org unit's unique identifier.
        db (Session): Database session for current request.

    Returns:
        OrgUnitExtended: The retrieved org unit.

    """
    org_unit = org_unit_repository.get_org_unit_by_id(id, db)
    org_unit_services.validate_org_unit_exists(org_unit)

    return org_unit


@router.get(
    "/{id}/employees",
    status_code=status.HTTP_200_OK,
    response_model=list[EmployeeExtended],
)
def get_employees_by_department(
    id: int,
    db: Session = Depends(get_db),
):
    """Retrieve all employees for a given department.

    Args:
        id (int): The department's unique identifier.
        db (Session): Database session for current request.

    Returns:
        list[EmployeeExtended]: The retrieved employees for the given org unit.

    """
    org_unit = get_org_unit(id, db)
    org_unit_services.validate_org_unit_exists(org_unit)

    return org_unit.employees


@router.get(
    "/{id}/holidays",
    status_code=status.HTTP_200_OK,
    response_model=list[HolidayExtended],
)
def get_holidays_by_department(
    id: int,
    db: Session = Depends(get_db),
):
    """Retrieve all holidays for a given department.

    Args:
        id (int): The department's unique identifier.
        db (Session): Database session for current request.

    Returns:
        list[HolidayExtended]: The retrieved holidays for the given org unit.

    """
    org_unit = get_org_unit(id, db)
    org_unit_services.validate_org_unit_exists(org_unit)

    return org_unit.holidays


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=OrgUnitExtended,
)
def update_org_unit(
    id: int,
    request: OrgUnitExtended,
    db: Session = Depends(get_db),
):
    """Update data for org unit with provided id.

    Args:
        id (int): The org unit's unique identifier.
        request (OrgUnitBase): Request data to update org_unit.
        db (Session): Database session for current request.

    Returns:
        OrgUnitExtended: The updated org unit.

    """
    common_services.validate_ids_match(request.org_unit_id, id)
    org_unit = org_unit_repository.get_org_unit_by_id(id, db)
    org_unit_services.validate_org_unit_exists(org_unit)
    org_unit_with_same_name = org_unit_repository.get_org_unit_by_name(
        request.name, db
    )
    org_unit_services.validate_org_unit_name_is_unique(
        org_unit_with_same_name, id
    )

    return org_unit_repository.update_org_unit(org_unit, request, db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_org_unit(id: int, db: Session = Depends(get_db)):
    """Delete org unit with provided id.

    Args:
        id (int): The org unit's unique identifier.
        db (Session): Database session for current request.

    """
    org_unit = org_unit_repository.get_org_unit_by_id(id, db)
    org_unit_services.validate_org_unit_exists(org_unit)
    org_unit_services.validate_org_unit_employees_list_is_empty(org_unit)
    org_unit_services.validate_org_unit_holidays_list_is_empty(org_unit)

    org_unit_repository.delete_org_unit(org_unit, db)
