"""Module defining API for employee-related operations."""

from fastapi import APIRouter, Depends, Request, Security, status
from sqlalchemy.orm import Session

import src.employee.repository as employee_repository
import src.user.routes as user_routes
from src.constants import EXC_MSG_IDS_DO_NOT_MATCH
from src.database import get_db
from src.employee.constants import (
    BASE_URL,
    EXC_MSG_EMPLOYEE_NOT_FOUND,
    EXC_MSG_EMPLOYEE_WITH_SAME_ID_EXISTS,
    IDENTIFIER,
)
from src.employee.schemas import EmployeeBase
from src.services import create_event_log, requires_permission, validate

router = APIRouter(prefix=BASE_URL, tags=["employee"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=EmployeeBase,
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
        EmployeeBase: The created employee.

    """
    duplicate_employee = employee_repository.get_employee_by_id(request.id, db)
    validate(
        duplicate_employee is None,
        EXC_MSG_EMPLOYEE_WITH_SAME_ID_EXISTS,
        status.HTTP_409_CONFLICT,
    )

    employee = employee_repository.create_employee(request, db)
    log_args = {"id": request.id}
    create_event_log(IDENTIFIER, "CREATE", log_args, caller_id, db)
    return employee


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[EmployeeBase],
)
def get_employees(
    db: Session = Depends(get_db),
    caller_id: int = Security(requires_permission, scopes=["employee.read"]),
):
    """Retrieve all employee data.

    Args:
        db (Session): Database session for current request.

    Returns:
        list[EmployeeBase]: The retrieved employees.

    """
    return employee_repository.get_employees(db)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=EmployeeBase,
)
def get_employee_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(requires_permission, scopes=["employee.read"]),
):
    """Retrieve data for employee with provided id.

    Args:
        id (int): Employee's id.
        db (Session): Database session for current request.

    Returns:
        EmployeeBase: The retrieved employee.

    """
    employee = employee_repository.get_employee_by_id(id, db)
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
    caller_id: int = Security(requires_permission, scopes=["employee.read"]),
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
    caller_id: int = Security(requires_permission, scopes=["employee.read"]),
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
    caller_id: int = Security(requires_permission, scopes=["employee.read"]),
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
    caller_id: int = Security(requires_permission, scopes=["employee.read"]),
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
    response_model=EmployeeBase,
)
def update_employee_by_id(
    id: int,
    request: EmployeeBase,
    db: Session = Depends(get_db),
    caller_id: int = Security(requires_permission, scopes=["employee.update"]),
):
    """Update data for employee with provided id.

    Args:
        id (int): Employee's id.
        request (EmployeeBase): Request data to update employee.
        db (Session): Database session for current request.

    Returns:
        EmployeeBase: The updated employee.

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
    log_args = {"id": request.id}
    create_event_log(IDENTIFIER, "UPDATE", log_args, caller_id, db)
    return employee


@router.put(
    "/{id}/change_id/{new_id}",
    status_code=status.HTTP_200_OK,
    response_model=EmployeeBase,
)
def update_employee_id(
    id: int,
    new_id: int,
    request: Request,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["employee.update.id"]
    ),
):
    """Update employee's id.

    Args:
        id (int): Employee's current id.
        new_id (int): Employee's new id.
        db (Session): Database session for current request.

    Returns:
        EmployeeBase: The updated employee.

    """
    employee = employee_repository.get_employee_by_id(id, db)
    validate(
        employee,
        EXC_MSG_EMPLOYEE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    duplicate_employee = employee_repository.get_employee_by_id(new_id, db)
    validate(
        duplicate_employee is None,
        EXC_MSG_EMPLOYEE_WITH_SAME_ID_EXISTS,
        status.HTTP_409_CONFLICT,
    )

    if caller_id == id:
        user_routes.logout(request, db)

    employee = employee_repository.update_employee_id(employee, new_id, db)
    log_args = {"id": id, "new_id": new_id}
    user_id = new_id if caller_id == id else caller_id
    create_event_log(IDENTIFIER, "UPDATE_ID", log_args, user_id, db)
    return employee


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(requires_permission, scopes=["employee.delete"]),
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
    log_args = {"id": employee.id}
    create_event_log(IDENTIFIER, "DELETE", log_args, caller_id, db)
