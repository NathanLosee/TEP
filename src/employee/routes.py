"""Module defining API for employee-related operations."""

from fastapi import APIRouter, Depends, Request, Security, status
from sqlalchemy.orm import Session

import src.employee.repository as employee_repository
import src.user.routes as user_routes
from src.constants import EXC_MSG_IDS_DO_NOT_MATCH
from src.database import get_db
from src.employee.constants import (
    BASE_URL,
    EXC_MSG_BADGE_NUMBER_EXISTS,
    EXC_MSG_EMPLOYEE_NOT_FOUND,
    IDENTIFIER,
)
from src.employee.schemas import EmployeeBase, EmployeeExtended, EmployeeUpdate
from src.services import create_event_log, requires_permission, validate

router = APIRouter(prefix=BASE_URL, tags=["employee"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=EmployeeExtended,
)
def create_employee(
    request: EmployeeBase,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["employee.create"]
    ),
):
    """Insert new employee data.

    Args:
        request (EmployeeBase): Request data for new employee.
        db (Session): Database session for current request.

    Returns:
        EmployeeExtended: The created employee.

    """
    duplicate_employee = employee_repository.get_employee_by_badge_number(
        request.badge_number, db
    )
    validate(
        duplicate_employee is None,
        EXC_MSG_BADGE_NUMBER_EXISTS,
        status.HTTP_409_CONFLICT,
    )

    employee = employee_repository.create_employee(request, db)
    log_args = {"badge_number": employee.badge_number}
    create_event_log(IDENTIFIER, "CREATE", log_args, caller_badge, db)
    return employee


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[EmployeeExtended],
)
def get_employees(
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["employee.read"]
    ),
):
    """Retrieve all employee data.

    Args:
        db (Session): Database session for current request.

    Returns:
        list[EmployeeExtended]: The retrieved employees.

    """
    return employee_repository.get_employees(db)


@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=list[EmployeeExtended],
)
def search_for_employees(
    department_name: str | None = None,
    org_unit_name: str | None = None,
    holiday_group_name: str | None = None,
    badge_number: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["employee.read"]
    ),
):
    """Search for employees based on various criteria.

    Args:
        department_name (str | None): Name of the department.
        org_unit_name (str | None): Name of the org unit.
        holiday_group_name (str | None): Name of the holiday group.
        badge_number (str | None): Employee's badge number.
        first_name (str | None): Employee's first name.
        last_name (str | None): Employee's last name.
        db (Session): Database session for current request.

    Returns:
        list[EmployeeExtended]: The retrieved employees.

    """
    employees = employee_repository.search_for_employees(
        db,
        department_name,
        org_unit_name,
        holiday_group_name,
        badge_number,
        first_name,
        last_name,
    )

    return employees


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=EmployeeExtended,
)
def get_employee_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["employee.read"]
    ),
):
    """Retrieve data for employee with provided id.

    Args:
        id (int): Employee's id.
        db (Session): Database session for current request.

    Returns:
        EmployeeExtended: The retrieved employee.

    """
    employee = employee_repository.get_employee_by_id(id, db)
    validate(
        employee,
        EXC_MSG_EMPLOYEE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return employee


@router.get(
    "/badge/{badge_number}",
    status_code=status.HTTP_200_OK,
    response_model=EmployeeExtended,
)
def get_employee_by_badge_number(
    badge_number: str,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["employee.read"]
    ),
):
    """Retrieve data for employee with provided badge number.

    Args:
        badge_number (str): Employee's badge number.
        db (Session): Database session for current request.

    Returns:
        EmployeeExtended: The retrieved employee.

    """
    employee = employee_repository.get_employee_by_badge_number(
        badge_number, db
    )
    validate(
        employee,
        EXC_MSG_EMPLOYEE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return employee


@router.get(
    "/{id}/departments",
    status_code=status.HTTP_200_OK,
)
def get_employee_departments(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["employee.read"]
    ),
):
    """Retrieve departments for employee with provided id.

    Args:
        id (int): Employee's id.
        db (Session): Database session for current request.

    Returns:
        list[str]: The retrieved department names.

    """
    employee = employee_repository.get_employee_by_id(id, db)
    validate(
        employee,
        EXC_MSG_EMPLOYEE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return [department.name for department in employee.departments]


@router.get(
    "/{id}/manager",
    status_code=status.HTTP_200_OK,
)
def get_employee_manager(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["employee.read"]
    ),
):
    """Retrieve manager for employee with provided id.

    Args:
        id (int): Employee's id.
        db (Session): Database session for current request.

    Returns:
        dict: The retrieved manager's first and last name.

    """
    employee = employee_repository.get_employee_by_id(id, db)
    validate(
        employee,
        EXC_MSG_EMPLOYEE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    manager = employee_repository.get_employee_by_id(employee.manager_id, db)
    validate(
        manager,
        EXC_MSG_EMPLOYEE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return {
        "first_name": manager.first_name,
        "last_name": manager.last_name,
    }


@router.get(
    "/{id}/org_unit",
    status_code=status.HTTP_200_OK,
)
def get_employee_org_unit(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["employee.read"]
    ),
):
    """Retrieve org unit name for employee with provided id.

    Args:
        id (int): Employee's id.
        db (Session): Database session for current request.

    Returns:
        str: The retrieved org unit's name.

    """
    employee = employee_repository.get_employee_by_id(id, db)
    validate(
        employee,
        EXC_MSG_EMPLOYEE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return employee.org_unit.name


@router.get(
    "/{id}/holiday_group",
    status_code=status.HTTP_200_OK,
)
def get_employee_holiday_group(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["employee.read"]
    ),
):
    """Retrieve holiday group for employee with provided id.

    Args:
        id (int): Employee's id.
        db (Session): Database session for current request.

    Returns:
        str: The retrieved holiday group's name.

    """
    employee = employee_repository.get_employee_by_id(id, db)
    validate(
        employee,
        EXC_MSG_EMPLOYEE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return employee.holiday_group.name


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=EmployeeExtended,
)
def update_employee_by_id(
    id: int,
    request: EmployeeUpdate,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["employee.update"]
    ),
):
    """Update data for employee with provided id.

    Args:
        id (int): Employee's id.
        request (EmployeeBase): Request data to update employee.
        db (Session): Database session for current request.

    Returns:
        EmployeeExtended: The updated employee.

    """
    validate(
        request.id == id,
        EXC_MSG_IDS_DO_NOT_MATCH,
        status.HTTP_400_BAD_REQUEST,
    )

    employee = employee_repository.get_employee_by_id(id, db)
    validate(
        employee,
        EXC_MSG_EMPLOYEE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    employee = employee_repository.update_employee_by_id(employee, request, db)
    log_args = {"badge_number": employee.badge_number}
    create_event_log(IDENTIFIER, "UPDATE", log_args, caller_badge, db)
    return employee


@router.put(
    "/{id}/badge_number",
    status_code=status.HTTP_200_OK,
    response_model=EmployeeExtended,
)
def update_employee_badge_number(
    id: int,
    badge_number: str,
    request: Request,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["employee.update.badge_number"]
    ),
):
    """Update employee's badge number.

    Args:
        id (int): Employee's current id.
        badge_number (str): Employee's new badge number.
        db (Session): Database session for current request.

    Returns:
        EmployeeExtended: The updated employee.

    """
    employee = employee_repository.get_employee_by_id(id, db)
    validate(
        employee,
        EXC_MSG_EMPLOYEE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    duplicate_employee = employee_repository.get_employee_by_badge_number(
        badge_number, db
    )
    validate(
        duplicate_employee is None,
        EXC_MSG_BADGE_NUMBER_EXISTS,
        status.HTTP_409_CONFLICT,
    )

    if caller_badge == id:
        user_routes.logout(request, db)

    employee = employee_repository.update_employee_badge_number(
        employee, badge_number, db
    )
    log_args = {
        "badge_number": employee.badge_number,
        "new_badge_number": badge_number,
    }
    create_event_log(IDENTIFIER, "UPDATE_BADGE", log_args, caller_badge, db)
    return employee


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["employee.delete"]
    ),
):
    """Delete employee data with provided id.

    Args:
        id (int): Employee's id.
        db (Session): Database session for current request.

    """
    employee = employee_repository.get_employee_by_id(id, db)
    validate(
        employee,
        EXC_MSG_EMPLOYEE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    employee_repository.delete_employee(employee, db)
    log_args = {"badge_number": employee.badge_number}
    create_event_log(IDENTIFIER, "DELETE", log_args, caller_badge, db)
