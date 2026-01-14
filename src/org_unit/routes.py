"""Module defining API for org unit-related operations."""

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

from src.constants import EXC_MSG_IDS_DO_NOT_MATCH
from src.database import get_db
from src.employee.schemas import EmployeeExtended
from src.org_unit.constants import (
    BASE_URL,
    EXC_MSG_EMPLOYEES_ASSIGNED,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_ORG_NOT_FOUND,
    IDENTIFIER,
)
from src.org_unit.repository import (
    create_org_unit as create_org_unit_in_db,
    delete_org_unit as delete_org_unit_from_db,
    get_org_unit_by_id,
    get_org_unit_by_name,
    get_org_units,
    update_org_unit as update_org_unit_in_db,
)
from src.org_unit.schemas import OrgUnitBase, OrgUnitExtended
from src.services import create_event_log, requires_license, requires_permission, validate

router = APIRouter(prefix=BASE_URL, tags=["org_unit"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=OrgUnitExtended,
)
def create_org_unit(
    request: OrgUnitBase,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["org_unit.create"]
    ),
):
    """Insert new org unit.

    Args:
        request (OrgUnitBase): Request data for new org unit.
        db (Session): Database session for current request.

    Returns:
        OrgUnitExtended: The created org unit.

    """
    duplicate_org_unit = get_org_unit_by_name(request.name, db)
    validate(
        duplicate_org_unit is None,
        EXC_MSG_NAME_ALREADY_EXISTS,
        status.HTTP_409_CONFLICT,
    )

    org_unit = create_org_unit_in_db(request, db)
    log_args = {"org_unit_name": org_unit.name}
    create_event_log(IDENTIFIER, "CREATE", log_args, caller_badge, db)
    return org_unit


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[OrgUnitExtended],
)
def get_org_units(
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["org_unit.read"]
    ),
):
    """Retrieve all org units.

    Args:
        db (Session): Database session for current request.

    Returns:
        list[OrgUnitExtended]: The retrieved org units.

    """
    return get_org_units(db)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=OrgUnitExtended,
)
def get_org_unit(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["org_unit.read"]
    ),
):
    """Retrieve data for org unit with provided id.

    Args:
        id (int): Org unit's unique identifier.
        db (Session): Database session for current request.

    Returns:
        OrgUnitExtended: The retrieved org unit.

    """
    org_unit = get_org_unit_by_id(id, db)
    validate(
        org_unit,
        EXC_MSG_ORG_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return org_unit


@router.get(
    "/{id}/employees",
    status_code=status.HTTP_200_OK,
    response_model=list[EmployeeExtended],
)
def get_employees_by_org_unit(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["org_unit.read", "employee.read"]
    ),
):
    """Retrieve all employees for a given org unit.

    Args:
        id (int): Org unit's unique identifier.
        db (Session): Database session for current request.

    Returns:
        list[EmployeeExtended]: The retrieved employees for the given org unit.

    """
    org_unit = get_org_unit(id, db)
    validate(
        org_unit,
        EXC_MSG_ORG_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return org_unit.employees


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=OrgUnitExtended,
)
def update_org_unit(
    id: int,
    request: OrgUnitExtended,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["org_unit.update"]
    ),
):
    """Update data for org unit with provided id.

    Args:
        id (int): Org unit's unique identifier.
        request (OrgUnitBase): Request data to update org_unit.
        db (Session): Database session for current request.

    Returns:
        OrgUnitExtended: The updated org unit.

    """
    validate(
        request.id == id,
        EXC_MSG_IDS_DO_NOT_MATCH,
        status.HTTP_400_BAD_REQUEST,
    )

    org_unit = get_org_unit_by_id(id, db)
    validate(
        org_unit,
        EXC_MSG_ORG_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    duplicate_org_unit = get_org_unit_by_name(request.name, db)
    validate(
        duplicate_org_unit is None or duplicate_org_unit.id == id,
        EXC_MSG_NAME_ALREADY_EXISTS,
        status.HTTP_409_CONFLICT,
    )

    org_unit = update_org_unit_in_db(org_unit, request, db)
    log_args = {"org_unit_name": org_unit.name}
    create_event_log(IDENTIFIER, "UPDATE", log_args, caller_badge, db)
    return org_unit


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_org_unit(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["org_unit.delete"]
    ),
):
    """Delete org unit with provided id.

    Args:
        id (int): Org unit's unique identifier.
        db (Session): Database session for current request.

    """
    org_unit = get_org_unit_by_id(id, db)
    validate(
        org_unit,
        EXC_MSG_ORG_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )
    validate(
        len(org_unit.employees) == 0,
        EXC_MSG_EMPLOYEES_ASSIGNED,
        status.HTTP_409_CONFLICT,
    )

    delete_org_unit_from_db(org_unit, db)
    log_args = {"org_unit_name": org_unit.name}
    create_event_log(IDENTIFIER, "DELETE", log_args, caller_badge, db)
