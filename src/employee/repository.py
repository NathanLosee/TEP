"""Module providing database interactivity for employee-related operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.auth_role.models import AuthRoleMembership
from src.department.models import DepartmentMembership
from src.employee.models import Employee
from src.employee.schemas import EmployeeBase
from src.event_log.models import EventLog
from src.timeclock.models import TimeclockEntry
from src.user.models import User


def create_employee(request: EmployeeBase, db: Session) -> Employee:
    """Insert new employee data.

    Args:
        request (EmployeeBase): Request data for new employee.
        db (Session): Database session for the current request.

    Returns:
        Employee: The created employee.

    """
    employee = Employee(**request.model_dump())
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
    return list(db.scalars(select(Employee)).all())


def get_employee_by_id(id: int, db: Session) -> Employee | None:
    """Retrieve an employee by a provided id.

    Args:
        id (int): Employee's unique identifier.
        db (Session): Database session for the current request.

    Returns:
        (Employee | None): The employee with the provided id, or
            None if not found.

    """
    return db.get(Employee, id)


def update_employee_by_id(
    employee: Employee, request: EmployeeBase, db: Session
) -> Employee:
    """Update an employee's existing data.

    Args:
        employee (Employee): Employee data to be updated.
        request (EmployeeBase): Request data for updating employee.
        db (Session): Database session for the current request.

    Returns:
        Employee: The updated employee.

    """
    employee_update = Employee(**request.model_dump())
    db.merge(employee_update)
    db.commit()
    db.refresh(employee)
    return employee


def update_employee_id(
    employee: Employee, new_id: int, db: Session
) -> Employee:
    """Update an employee's id.
    This function updates the employee's id and all related
    records in the database, including department memberships,
    timeclock entries, user account, event logs, auth role memberships.

    Args:
        employee (Employee): Employee data to be updated.
        new_id (int): New id for the employee.
        db (Session): Database session for the current request.

    Returns:
        Employee: The updated employee.

    """
    old_id = employee.id

    employee.id = new_id

    department_memberships = db.scalars(
        select(DepartmentMembership).where(
            DepartmentMembership.employee_id == old_id
        )
    ).all()
    for membership in department_memberships:
        membership.employee_id = new_id

    timeclock_entries = db.scalars(
        select(TimeclockEntry).where(TimeclockEntry.employee_id == old_id)
    ).all()
    for entry in timeclock_entries:
        entry.employee_id = new_id

    user = db.get(User, old_id)
    if user:
        user.id = new_id

        auth_role_memberships = db.scalars(
            select(AuthRoleMembership).where(
                AuthRoleMembership.user_id == old_id
            )
        ).all()
        for membership in auth_role_memberships:
            membership.user_id = new_id

        event_logs = db.scalars(
            select(EventLog).where(EventLog.user_id == old_id)
        ).all()
        for log in event_logs:
            log.user_id = new_id

    db.commit()
    db.refresh(employee)
    return employee


def delete_employee(employee: Employee, db: Session) -> None:
    """Delete provided employee data.

    Args:
        employee (Employee): Employee data to be delete.
        db (Session): Database session for the current request.

    """
    db.delete(employee)
    db.commit()
