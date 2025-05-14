"""Module defining API for employee-related operations."""

from fastapi import APIRouter, Security, status, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.login.services import requires_permission
import src.services as common_services
from src.employee.constants import BASE_URL, IDENTIFIER
import src.employee.repository as employee_repository
import src.employee.services as employee_services
from src.employee.schemas import (
    EmployeeBase,
    EmployeeExtended,
)
from src.auth_role.schemas import AuthRoleExtended
from src.org_unit.schemas import OrgUnitExtended
from src.holiday_group.schemas import HolidayGroupExtended
from src.department.schemas import DepartmentExtended
from src.event_log.constants import EVENT_LOG_MSGS
import src.event_log.routes as event_log_routes
from src.event_log.schemas import EventLogBase

router = APIRouter(prefix=BASE_URL, tags=["employee"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=EmployeeExtended,
)
def create_employee(
    request: EmployeeBase,
    db: Session = Depends(get_db),
    caller_id: int = Security(requires_permission, scopes=["employee.create"]),
):
    """Insert new employee data.

    Args:
        request (EmployeeBase): Request data for new employee.
        db (Session): Database session for current request.

    Returns:
        EmployeeExtended: Response containing newly created employee data.

    """
    employee = employee_repository.create_employee(request, db)
    event_log_routes.create_event_log(
        EventLogBase(
            log=EVENT_LOG_MSGS[IDENTIFIER]["CREATE"].format(
                employee_id=employee.id
            ),
            employee_id=caller_id,
        ),
        db,
    )
    employee.password = None  # Remove password from response
    return employee


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[EmployeeExtended],
)
def get_employees(
    db: Session = Depends(get_db),
    caller_id: int = Security(requires_permission, scopes=["employee.read"]),
):
    """Retrieve all employee data.

    Args:
        db (Session): Database session for current request.

    Returns:
        list[EmployeeExtended]: The retrieved employees.

    """
    return employee_repository.get_employees(db)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=EmployeeExtended,
)
def get_employee_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(requires_permission, scopes=["employee.read"]),
):
    """Retrieve data for employee with provided id.

    Args:
        id (int): The employee's unique identifier.
        db (Session): Database session for current request.

    Returns:
        EmployeeExtended: The retrieved employee.

    """
    employee = employee_repository.get_employee_by_id(id, db)
    employee_services.validate_employee_exists(employee)

    return employee


@router.get(
    "/{id}/auth_roles",
    status_code=status.HTTP_200_OK,
    response_model=list[AuthRoleExtended],
)
def get_employee_auth_roles(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["employee.read", "auth_role.read"]
    ),
):
    """Retrieve auth roles for employee with provided id.

    Args:
        id (int): The employee's unique identifier.
        db (Session): Database session for current request.

    Returns:
        list[AuthRoleExtended]: The retrieved auth roles.

    """
    employee = employee_repository.get_employee_by_id(id, db)
    employee_services.validate_employee_exists(employee)

    return employee.auth_roles


@router.get(
    "/{id}/org_unit",
    status_code=status.HTTP_200_OK,
    response_model=OrgUnitExtended,
)
def get_employee_org_unit(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["employee.read", "org_unit.read"]
    ),
):
    """Retrieve org unit for employee with provided id.

    Args:
        id (int): The employee's unique identifier.
        db (Session): Database session for current request.

    Returns:
        OrgUnitExtended: The retrieved org unit.

    """
    employee = employee_repository.get_employee_by_id(id, db)
    employee_services.validate_employee_exists(employee)

    return employee.org_unit


@router.get(
    "/{id}/holiday_group",
    status_code=status.HTTP_200_OK,
    response_model=HolidayGroupExtended,
)
def get_employee_holiday_group(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["employee.read", "holiday_group.read"]
    ),
):
    """Retrieve holiday group for employee with provided id.

    Args:
        id (int): The employee's unique identifier.
        db (Session): Database session for current request.

    Returns:
        HolidayGroupExtended: The retrieved holiday group.

    """
    employee = employee_repository.get_employee_by_id(id, db)
    employee_services.validate_employee_exists(employee)

    return employee.holiday_group


@router.get(
    "/{id}/departments",
    status_code=status.HTTP_200_OK,
    response_model=list[DepartmentExtended],
)
def get_employee_departments(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["employee.read", "department.read"]
    ),
):
    """Retrieve departments for employee with provided id.

    Args:
        id (int): The employee's unique identifier.
        db (Session): Database session for current request.

    Returns:
        list[DepartmentExtended]: The retrieved departments.

    """
    employee = employee_repository.get_employee_by_id(id, db)
    employee_services.validate_employee_exists(employee)

    return employee.departments


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=EmployeeExtended,
)
def update_employee_by_id(
    id: int,
    request: EmployeeExtended,
    db: Session = Depends(get_db),
    caller_id: int = Security(requires_permission, scopes=["employee.update"]),
):
    """Update data for employee with provided id.

    Args:
        id (int): The employee's unique identifier.
        request (EmployeeBase): Request data to update employee.
        db (Session): Database session for current request.

    Returns:
        EmployeeExtended: The updated employee.

    """
    common_services.validate_ids_match(request.id, id)
    employee = employee_repository.get_employee_by_id(id, db)
    employee_services.validate_employee_exists(employee)

    employee = employee_repository.update_employee_by_id(employee, request, db)
    employee.password = None  # Remove password from response
    event_log_routes.create_event_log(
        EventLogBase(
            log=EVENT_LOG_MSGS[IDENTIFIER]["UPDATE"].format(
                employee_id=employee.id
            ),
            employee_id=caller_id,
        ),
        db,
    )
    return employee


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(requires_permission, scopes=["employee.delete"]),
):
    """Delete employee data with provided id.

    Args:
        id (int): The employee's unique identifier.
        db (Session): Database session for current request.

    """
    employee = employee_repository.get_employee_by_id(id, db)
    employee_services.validate_employee_exists(employee)

    employee_repository.delete_employee(employee, db)
    event_log_routes.create_event_log(
        EventLogBase(
            log=EVENT_LOG_MSGS[IDENTIFIER]["DELETE"].format(
                employee_id=employee.id
            ),
            employee_id=caller_id,
        ),
        db,
    )
