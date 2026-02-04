"""Module providing database interactions for department-related operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.department.models import Department, DepartmentMembership
from src.department.schemas import DepartmentBase, DepartmentExtended


def create_department(request: DepartmentBase, db: Session) -> Department:
    """Insert new department data.

    Args:
        request (DepartmentBase): Request data for new department.
        db (Session): Database session for the current request.

    Returns:
        Org_unit: The created department.

    """
    department = Department(**request.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


def create_membership(
    department_id: int, employee_id: int, db: Session
) -> Department:
    """Insert new membership data.

    Args:
        department_id (int): Department in the membership.
        employee_id (int): Employee in the membership.
        db (Session): Database session for the current request.

    Returns:
        Department: The department with updated membership.

    """
    membership = DepartmentMembership(
        department_id=department_id,
        employee_id=employee_id,
    )
    db.add(membership)
    db.commit()
    return get_department_by_id(department_id, db)


def get_departments(db: Session) -> list[Department]:
    """Retrieve all department data.

    Args:
        db (Session): Database session for the current request.

    Returns:
        list[Department]: The retrieved departments.

    """
    return db.scalars(select(Department)).all()


def get_department_by_id(id: int, db: Session) -> Department | None:
    """Retrieve an department by a provided id.

    Args:
        id (int): Department's unique identifier.
        db (Session): Database session for the current request.

    Returns:
        (Department | None): The department with the provided id, or
            None if not found.

    """
    return db.get(Department, id)


def get_department_by_name(name: str, db: Session) -> Department | None:
    """Retrieve an department by a provided name.

    Args:
        name (str): Department's name.
        db (Session): Database session for the current request.

    Returns:
        (Department | None): The department with the provided name, or
            None if not found.

    """
    return db.scalars(
        select(Department).where(Department.name == name)
    ).first()


def update_department(
    department: Department, request: DepartmentExtended, db: Session
) -> Department:
    """Update an department's existing data.

    Args:
        department (Department): Department data to be updated.
        request (DepartmentExtended): Request data for updating department.
        db (Session): Database session for the current request.

    Returns:
        Department: The updated department.

    """
    department.name = request.name
    db.add(department)
    db.commit()
    return department


def delete_department(department: Department, db: Session):
    """Delete an department's data.

    Args:
        department (Department): Department data to be deleted.
        db (Session): Database session for the current request.

    """
    db.delete(department)
    db.commit()


def delete_membership(
    department_id: int, employee_id: int, db: Session
) -> Department:
    """Delete a membership's data.

    Args:
        department_id (int): Department in the membership.
        employee_id (int): Employee in the membership.
        db (Session): Database session for the current request.

    Returns:
        Department: The department with updated membership.

    """
    membership = db.scalars(
        select(DepartmentMembership)
        .where(DepartmentMembership.department_id == department_id)
        .where(DepartmentMembership.employee_id == employee_id)
    ).first()
    db.delete(membership)
    db.commit()
    return get_department_by_id(department_id, db)
