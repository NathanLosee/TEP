"""Module defining API for auth role-related operations."""

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
import src.services as common_services
from src.database import get_db
import src.employee.routes as employee_routes
from src.employee.schemas import EmployeeExtended
from src.auth_role.constants import BASE_URL
import src.auth_role.repository as auth_role_repository
import src.auth_role.services as auth_role_services
from src.auth_role.schemas import AuthRoleBase, AuthRoleExtended

router = APIRouter(prefix=BASE_URL, tags=["auth_role"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthRoleExtended,
)
def create_auth_role(request: AuthRoleBase, db: Session = Depends(get_db)):
    """Insert new auth role.

    Args:
        request (AuthRoleBase): Request data for new auth role.
        db (Session): Database session for current request.

    Returns:
        AuthRoleExtended: Response containing newly created auth role
            data.

    """
    auth_role_with_same_name = auth_role_repository.get_auth_role_by_name(
        request.name, db
    )
    auth_role_services.validate_auth_role_name_is_unique(
        auth_role_with_same_name, None
    )

    return auth_role_repository.create_auth_role(request, db)


@router.post(
    "/{auth_role_id}/employees/{employee_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=list[EmployeeExtended],
)
def create_auth_role_membership(
    auth_role_id: int, employee_id: int, db: Session = Depends(get_db)
):
    """Insert new membership.

    Args:
        auth_role_id (int): The auth role's unique identifier.
        employee_id (int): The employee's unique identifier.
        db (Session): Database session for current request.

    Returns:
        list[AuthRoleExtended]: The updated list of auth roles for the
            employee.

    """
    auth_role = auth_role_repository.get_auth_role_by_id(auth_role_id, db)
    auth_role_services.validate_auth_role_exists(auth_role)
    employee = employee_routes.get_employee_by_id(employee_id, db)
    auth_role_services.validate_employee_should_have_auth_role(
        auth_role, employee, False
    )

    auth_role = auth_role_repository.create_membership(
        auth_role_id, employee_id, db
    )
    return auth_role.employees


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[AuthRoleExtended],
)
def get_auth_roles(
    db: Session = Depends(get_db),
):
    """Retrieve all auth roles.

    Args:
        db (Session): Database session for current request.

    Returns:
        list[AuthRoleExtended]: The retrieved auth roles.

    """
    return auth_role_repository.get_auth_roles(db)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=AuthRoleExtended,
)
def get_auth_role(id: int, db: Session = Depends(get_db)):
    """Retrieve data for auth role with provided id.

    Args:
        id (int): The auth role's unique identifier.
        db (Session): Database session for current request.

    Returns:
        AuthRoleExtended: The retrieved auth role.

    """
    auth_role = auth_role_repository.get_auth_role_by_id(id, db)
    auth_role_services.validate_auth_role_exists(auth_role)

    return auth_role


@router.get(
    "/{id}/employees",
    status_code=status.HTTP_200_OK,
    response_model=list[EmployeeExtended],
)
def get_employees_by_auth_role(
    id: int,
    db: Session = Depends(get_db),
):
    """Retrieve all employees with a given auth role.

    Args:
        id (int): The auth role's unique identifier.
        db (Session): Database session for current request.

    Returns:
        list[EmployeeExtended]: The retrieved employees for the given
            auth role.

    """
    auth_role = get_auth_role(id, db)
    auth_role_services.validate_auth_role_exists(auth_role)

    return auth_role.employees


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=AuthRoleExtended,
)
def update_auth_role(
    id: int,
    request: AuthRoleExtended,
    db: Session = Depends(get_db),
):
    """Update data for auth role with provided id.

    Args:
        id (int): The auth role's unique identifier.
        request (AuthRoleExtended): Request data to update auth role.
        db (Session): Database session for current request.

    Returns:
        AuthRoleExtended: The updated auth role.

    """
    common_services.validate_ids_match(id, request.id)
    auth_role = auth_role_repository.get_auth_role_by_id(id, db)
    auth_role_services.validate_auth_role_exists(auth_role)
    auth_role_with_same_name = auth_role_repository.get_auth_role_by_name(
        request.name, db
    )
    auth_role_services.validate_auth_role_name_is_unique(
        auth_role_with_same_name, id
    )

    return auth_role_repository.update_auth_role(auth_role, request, db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_auth_role(id: int, db: Session = Depends(get_db)):
    """Delete auth role with provided id.

    Args:
        id (int): The auth role's unique identifier.
        db (Session): Database session for current request.

    """
    auth_role = auth_role_repository.get_auth_role_by_id(id, db)
    auth_role_services.validate_auth_role_exists(auth_role)

    auth_role_repository.delete_auth_role(auth_role, db)


@router.delete(
    "/{auth_role_id}/employees/{employee_id}",
    status_code=status.HTTP_200_OK,
    response_model=list[EmployeeExtended],
)
def delete_auth_role_membership(
    auth_role_id: int, employee_id: int, db: Session = Depends(get_db)
):
    """Delete membership.

    Args:
        auth_role_id (int): The auth role's unique identifier.
        employee_id (int): The employee's unique identifier.
        db (Session): Database session for current request.

    Returns:
        list[EmployeeExtended]: The updated list of employees for the
            auth role.

    """
    auth_role = auth_role_repository.get_auth_role_by_id(auth_role_id, db)
    auth_role_services.validate_auth_role_exists(auth_role)
    employee_with_auth_role = employee_routes.get_employee_by_id(
        employee_id, db
    )
    auth_role_services.validate_employee_should_have_auth_role(
        auth_role, employee_with_auth_role, True
    )

    auth_role = auth_role_repository.delete_membership(
        auth_role_id, employee_id, db
    )
    return auth_role.employees
