"""Module providing database interactivity for employee-related operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.department.models import Department
from src.employee.models import Employee
from src.employee.schemas import EmployeeBase
from src.holiday_group.models import HolidayGroup
from src.org_unit.models import OrgUnit


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
    return list(
        db.scalars(
            select(Employee)
            .options(
                selectinload(Employee.org_unit),
                selectinload(Employee.holiday_group),
                selectinload(Employee.departments),
            )
        ).all()
    )


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


def get_employee_by_badge_number(
    badge_number: str, db: Session
) -> Employee | None:
    """Retrieve an employee by a provided badge number.

    Args:
        badge_number (str): Employee's badge number.
        db (Session): Database session for the current request.

    Returns:
        (Employee | None): The employee with the provided badge number,
            or None if not found.

    """
    return db.scalar(
        select(Employee).where(Employee.badge_number == badge_number)
    )


def search_for_employees(
    db: Session,
    department_name: str | None = None,
    org_unit_name: str | None = None,
    holiday_group_name: str | None = None,
    badge_number: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
) -> list[Employee]:
    """Search for employees based on various criteria.

    Args:
        department_name (str | None): Department name to search for.
        org_unit_name (str | None): Org unit name to search for.
        holiday_group_name (str | None): Holiday group name to search
            for.
        badge_number (str | None): Badge number to search for.
        first_name (str | None): First name to search for.
        last_name (str | None): Last name to search for.
        db (Session): Database session for the current request.

    Returns:
        list[Employee]: The retrieved employees.

    """
    query = db.query(Employee).options(
        selectinload(Employee.org_unit),
        selectinload(Employee.holiday_group),
        selectinload(Employee.departments),
    )
    if department_name:
        query = query.filter(
            Employee.departments.has(Department.name.contains(department_name))
        )
    if org_unit_name:
        query = query.filter(
            Employee.org_unit.has(OrgUnit.name.contains(org_unit_name))
        )
    if holiday_group_name:
        query = query.filter(
            Employee.holiday_group.has(
                HolidayGroup.name.contains(holiday_group_name)
            )
        )
    if badge_number:
        query = query.filter(Employee.badge_number.contains(badge_number))
    if first_name:
        query = query.filter(Employee.first_name.contains(first_name))
    if last_name:
        query = query.filter(Employee.last_name.contains(last_name))

    return list(query.all())


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


def update_employee_badge_number(
    employee: Employee, new_number: str, db: Session
) -> Employee:
    """Update an employee's badge number.

    Args:
        employee (Employee): Employee data to be updated.
        new_number (str): New badge number for the employee.
        db (Session): Database session for the current request.

    Returns:
        Employee: The updated employee.

    """
    employee.badge_number = new_number
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
