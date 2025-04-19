"""Module providing database interactivity for employee-related operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.employee.models import Employee


def get_employee_by_id_and_password(
    db: Session,
    employee_id: int,
    password: str,
) -> Employee:
    """Retrieve an employee by ID and password.

    Args:
        db (Session): Database session.
        employee_id (int): The ID of the employee.
        password (str): The password of the employee.

    Returns:
        Employee: The employee object if found, None otherwise.
    """
    return db.scalars(
        select(Employee).where(
            Employee.id == employee_id,
            Employee.password == password,
        )
    ).first()
