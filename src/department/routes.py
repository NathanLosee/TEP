"""Module defining API for department-related operations."""

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

import src.department.repository as department_repository
import src.employee.routes as employee_routes
from src.constants import EXC_MSG_IDS_DO_NOT_MATCH
from src.database import get_db
from src.department.constants import (
    BASE_URL,
    EXC_MSG_DEPARTMENT_NOT_FOUND,
    EXC_MSG_EMPLOYEE_IS_MEMBER,
    EXC_MSG_EMPLOYEE_NOT_MEMBER,
    EXC_MSG_EMPLOYEES_ASSIGNED,
    EXC_MSG_NAME_ALREADY_EXISTS,
    IDENTIFIER,
    MEMBERSHIP_IDENTIFIER,
)
from src.department.schemas import DepartmentBase, DepartmentExtended
from src.employee.schemas import EmployeeBase
from src.services import create_event_log, requires_permission, validate

router = APIRouter(prefix=BASE_URL, tags=["department"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DepartmentExtended,
)
def create_department(
    request: DepartmentBase,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["department.create"]
    ),
):
    """Insert new department.

    Args:
        request (DepartmentBase): Request data for new department.
        db (Session): Database session for current request.

    Returns:
        DepartmentExtended: The created department.

    """
    duplicate_department = department_repository.get_department_by_name(
        request.name, db
    )
    validate(
        duplicate_department is None,
        EXC_MSG_NAME_ALREADY_EXISTS,
        status.HTTP_409_CONFLICT,
    )

    department = department_repository.create_department(request, db)
    log_args = {"department_name": department.name}
    create_event_log(IDENTIFIER, "CREATE", log_args, caller_id, db)
    return department


@router.post(
    "/{department_id}/employees/{employee_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=list[EmployeeBase],
)
def create_department_membership(
    department_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["department.assign", "employee.read"]
    ),
):
    """Insert new membership.

    Args:
        department_id (int): Department's unique identifier.
        employee_id (int): Employee's id.
        db (Session): Database session for current request.

    Returns:
        list[EmployeeBase]: The updated list of employees in the
            department.

    """
    department = department_repository.get_department_by_id(department_id, db)
    validate(
        department,
        EXC_MSG_DEPARTMENT_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    employee = employee_routes.get_employee_by_id(employee_id, db)
    validate(
        employee not in department.employees,
        EXC_MSG_EMPLOYEE_IS_MEMBER,
        status.HTTP_409_CONFLICT,
    )

    department = department_repository.create_membership(
        department_id, employee_id, db
    )
    log_args = {"department_name": department.name, "id": employee.id}
    create_event_log(MEMBERSHIP_IDENTIFIER, "CREATE", log_args, caller_id, db)
    return department.employees


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[DepartmentExtended],
)
def get_departments(
    db: Session = Depends(get_db),
    caller_id: int = Security(requires_permission, scopes=["department.read"]),
):
    """Retrieve all departments.

    Args:
        db (Session): Database session for current request.

    Returns:
        list[DepartmentExtended]: The retrieved departments.

    """
    return department_repository.get_departments(db)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=DepartmentExtended,
)
def get_department(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(requires_permission, scopes=["department.read"]),
):
    """Retrieve data for department with provided id.

    Args:
        id (int): Department's unique identifier.
        db (Session): Database session for current request.

    Returns:
        DepartmentExtended: The retrieved department.

    """
    department = department_repository.get_department_by_id(id, db)
    validate(
        department,
        EXC_MSG_DEPARTMENT_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return department


@router.get(
    "/{id}/employees",
    status_code=status.HTTP_200_OK,
    response_model=list[EmployeeBase],
)
def get_employees_by_department(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["department.read", "employee.read"]
    ),
):
    """Retrieve all employees for a given department.

    Args:
        id (int): Department's unique identifier.
        db (Session): Database session for current request.

    Returns:
        list[EmployeeBase]: The retrieved employees for the given
            department.

    """
    department = get_department(id, db)
    validate(
        department,
        EXC_MSG_DEPARTMENT_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return department.employees


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=DepartmentExtended,
)
def update_department(
    id: int,
    request: DepartmentExtended,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["department.update"]
    ),
):
    """Update data for department with provided id.

    Args:
        id (int): Department's unique identifier.
        request (DepartmentBase): Request data to update department.
        db (Session): Database session for current request.

    Returns:
        DepartmentExtended: The updated department.

    """
    validate(
        request.id == id,
        EXC_MSG_IDS_DO_NOT_MATCH,
        status.HTTP_400_BAD_REQUEST,
    )

    department = department_repository.get_department_by_id(id, db)
    validate(
        department,
        EXC_MSG_DEPARTMENT_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    duplicate_department = department_repository.get_department_by_name(
        request.name, db
    )
    validate(
        duplicate_department is None or duplicate_department.id == id,
        EXC_MSG_NAME_ALREADY_EXISTS,
        status.HTTP_409_CONFLICT,
    )

    department = department_repository.update_department(
        department, request, db
    )
    log_args = {"department_name": department.name}
    create_event_log(IDENTIFIER, "UPDATE", log_args, caller_id, db)
    return department


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_department(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["department.delete"]
    ),
):
    """Delete department with provided id.

    Args:
        id (int): Department's unique identifier.
        db (Session): Database session for current request.

    """
    department = department_repository.get_department_by_id(id, db)
    validate(
        department,
        EXC_MSG_DEPARTMENT_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )
    validate(
        len(department.employees) == 0,
        EXC_MSG_EMPLOYEES_ASSIGNED,
        status.HTTP_409_CONFLICT,
    )

    department_repository.delete_department(department, db)
    log_args = {"department_name": department.name}
    create_event_log(IDENTIFIER, "DELETE", log_args, caller_id, db)


@router.delete(
    "/{department_id}/employees/{employee_id}",
    status_code=status.HTTP_200_OK,
    response_model=list[EmployeeBase],
)
def delete_department_membership(
    department_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission,
        scopes=["department.unassign", "employee.read"],
    ),
):
    """Delete membership.

    Args:
        department_id (int): Department's unique identifier.
        employee_id (int): Employee's id.
        db (Session): Database session for current request.

    Returns:
        list[EmployeeBase]: The updated list of employees in the
            department.

    """
    department = department_repository.get_department_by_id(department_id, db)
    validate(
        department,
        EXC_MSG_DEPARTMENT_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    employee = employee_routes.get_employee_by_id(employee_id, db)
    validate(
        employee in department.employees,
        EXC_MSG_EMPLOYEE_NOT_MEMBER,
        status.HTTP_404_NOT_FOUND,
    )

    department = department_repository.delete_membership(
        department_id, employee_id, db
    )
    log_args = {"department_name": department.name, "id": employee.id}
    create_event_log(MEMBERSHIP_IDENTIFIER, "DELETE", log_args, caller_id, db)
    return department.employees
