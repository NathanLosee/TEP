"""Module providing database interactivity for employee-related operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.login.services import hash_password
from src.employee.models import Employee
from src.employee.schemas import (
    EmployeeBase,
    EmployeeExtended,
)


def create_employee(request: EmployeeBase, db: Session) -> Employee:
    """Insert new employee data.

    Args:
        request (EmployeeBase): Request data for new employee.
        db (Session): Database session for the current request.

    Returns:
        Employee: The created employee.

    """
    employee = Employee(**request.model_dump())
    if request.password:
        employee.password = hash_password(request.password)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def get_employees(db: Session) -> list[Employee]:
    """Retrieve all existing employees.

    Args:
        db (Session): Database session for the current request.

    Returns:
        list[Employee]: The retrieved employees.

    """
    return db.scalars(select(Employee)).all()


def get_employee_by_id(id: int, db: Session) -> Employee | None:
    """Retrieve a employee by a provided id.

    Args:
        id (int): The id of the employee to look for.
        db (Session): Database session for the current request.

    Returns:
        (Employee | None): The employee with the provided id, or None if not
            found.

    """
    return db.get(Employee, id)


def update_employee_by_id(
    employee: Employee, request: EmployeeExtended, db: Session
) -> Employee:
    """Update a employee's existing data.

    Args:
        employee (Employee): The employee data to be updated.
        request (EmployeeExtended): Request data for updating employee.
        db (Session): Database session for the current request.

    Returns:
        Employee: The updated employee.

    """
    employee_update = Employee(**request.model_dump())
    if request.password:
        employee_update.password = hash_password(request.password)
    db.merge(employee_update)
    db.commit()
    db.refresh(employee)
    return employee


def delete_employee(employee: Employee, db: Session) -> None:
    """Delete provided employee data.

    Args:
        employee (Employee): The employee data to be delete.
        db (Session): Database session for the current request.

    """
    db.delete(employee)
    db.commit()
