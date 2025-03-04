"""Module defining API for department-related operations."""

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from src.database import get_db
import src.employee.routes as employee_routes
from src.employee.schemas import EmployeeExtended
from src.job.schemas import JobExtended
import src.services as common_services
from src.department.constants import BASE_URL
import src.department.repository as department_repository
import src.department.services as department_services
from src.department.schemas import DepartmentBase, DepartmentExtended

router = APIRouter(prefix=BASE_URL, tags=["department"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DepartmentExtended,
)
def create_department(request: DepartmentBase, db: Session = Depends(get_db)):
    """Insert new department.

    Args:
        request (DepartmentBase): Request data for new department.
        db (Session): Database session for current request.

    Returns:
        DepartmentExtended: Response containing newly created department
            data.

    """
    department_with_same_name = department_repository.get_department_by_name(
        request.name, db
    )
    department_services.validate_department_name_is_unique(
        department_with_same_name
    )

    return department_repository.create_department(request, db)


@router.post(
    "/{department_id}/employees/{employee_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=DepartmentExtended,
)
def create_department_membership(
    department_id: int, employee_id: int, db: Session = Depends(get_db)
):
    """Insert new membership.

    Args:
        department_id (int): The department's unique identifier.
        employee_id (int): The employee's unique identifier.
        db (Session): Database session for current request.

    Returns:
        DepartmentExtended: The department data with new employee.

    """
    department = department_repository.get_department_by_id(department_id, db)
    department_services.validate_department_exists(department)
    employee = employee_routes.get_employee_by_id(employee_id, db)
    department_services.validate_employee_is_not_in_department(
        department, employee
    )

    return department_repository.create_membership(
        department_id, employee_id, db
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[DepartmentExtended],
)
def get_departments(
    db: Session = Depends(get_db),
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
    response_model=list[DepartmentExtended],
)
def get_department(id: int, db: Session = Depends(get_db)):
    """Retrieve data for department with provided id.

    Args:
        id (int): The department's unique identifier.
        db (Session): Database session for current request.

    Returns:
        DepartmentExtended: The retrieved department.

    """
    department = department_repository.get_department_by_id(id, db)
    department_services.validate_department_exists(department)

    return department


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
        list[EmployeeExtended]: The retrieved employees for the given
            department.

    """
    department = get_department(id, db)
    department_services.validate_department_exists(department)

    return department.employees


@router.get(
    "/{id}/jobs",
    status_code=status.HTTP_200_OK,
    response_model=list[JobExtended],
)
def get_jobs_by_department(
    id: int,
    db: Session = Depends(get_db),
):
    """Retrieve all jobs for a given department.

    Args:
        id (int): The department's unique identifier.
        db (Session): Database session for current request.

    Returns:
        list[JobExtended]: The retrieved jobs for the given department.

    """
    department = get_department(id, db)
    department_services.validate_department_exists(department)

    return department.jobs


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=DepartmentExtended,
)
def update_department(
    id: int,
    request: DepartmentExtended,
    db: Session = Depends(get_db),
):
    """Update data for department with provided id.

    Args:
        id (int): The department's unique identifier.
        request (DepartmentBase): Request data to update department.
        db (Session): Database session for current request.

    Returns:
        DepartmentExtended: The updated department.

    """
    common_services.validate_ids_match(request.department_id, id)
    department = department_repository.get_department_by_id(id, db)
    department_services.validate_department_exists(department)
    department_with_same_name = department_repository.get_department_by_name(
        request.name, db
    )
    department_services.validate_department_name_is_unique(
        department_with_same_name, id, db
    )

    return department_repository.update_department(department, request, db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(id: int, db: Session = Depends(get_db)):
    """Delete department with provided id.

    Args:
        id (int): The department's unique identifier.
        db (Session): Database session for current request.

    """
    department = department_repository.get_department_by_id(id, db)
    department_services.validate_department_exists(department)
    department_services.validate_department_employees_list_is_empty(department)
    department_services.validate_department_jobs_list_is_empty(department)

    department_repository.delete_department(department, db)


@router.delete(
    "/{department_id}/employees/{employee_id}",
    status_code=status.HTTP_200_OK,
    response_model=DepartmentExtended,
)
def delete_department_membership(
    department_id: int, employee_id: int, db: Session = Depends(get_db)
):
    """Delete membership.

    Args:
        department_id (int): The department's unique identifier.
        employee_id (int): The employee's unique identifier.
        db (Session): Database session for current request.

    Returns:
        DepartmentExtended: The department data without removed employee.

    """
    department = department_repository.get_department_by_id(department_id, db)
    department_services.validate_department_exists(department)
    employee = employee_routes.get_employee_by_id(employee_id, db)
    department_services.validate_employee_is_in_department(
        department, employee
    )

    return department_repository.delete_membership(
        department_id, employee_id, db
    )
