"""Module defining API for auth role-related operations."""

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

import src.auth_role.repository as auth_role_repository
import src.user.routes as user_routes
from src.auth_role.constants import (
    BASE_URL,
    EXC_MSG_AUTH_ROLE_NOT_FOUND,
    EXC_MSG_EMPLOYEE_IS_MEMBER,
    EXC_MSG_EMPLOYEE_NOT_MEMBER,
    EXC_MSG_EMPLOYEES_ASSIGNED,
    EXC_MSG_NAME_ALREADY_EXISTS,
    IDENTIFIER,
    MEMBERSHIP_IDENTIFIER,
)
from src.auth_role.schemas import AuthRoleBase, AuthRoleExtended
from src.constants import EXC_MSG_IDS_DO_NOT_MATCH
from src.database import get_db
from src.services import create_event_log, requires_permission, validate
from src.user.schemas import UserResponse

router = APIRouter(prefix=BASE_URL, tags=["auth_role"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthRoleExtended,
)
def create_auth_role(
    request: AuthRoleBase,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["auth_role.create"]
    ),
):
    """Insert new auth role.

    Args:
        request (AuthRoleBase): Request data for new auth role.
        db (Session): Database session for current request.

    Returns:
        AuthRoleExtended: The created auth role.

    """
    duplicate_auth_role = auth_role_repository.get_auth_role_by_name(
        request.name, db
    )
    validate(
        duplicate_auth_role is None,
        EXC_MSG_NAME_ALREADY_EXISTS,
        status.HTTP_409_CONFLICT,
    )

    auth_role = auth_role_repository.create_auth_role(request, db)
    log_args = {"auth_role_name": auth_role.name}
    create_event_log(IDENTIFIER, "CREATE", log_args, caller_id, db)
    return auth_role


@router.post(
    "/{auth_role_id}/users/{user_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=list[UserResponse],
)
def create_auth_role_membership(
    auth_role_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["auth_role.assign", "auth_role.unassign"]
    ),
):
    """Insert new membership.

    Args:
        auth_role_id (int): Auth role in the membership.
        user_id (int): User in the membership.
        db (Session): Database session for current request.

    Returns:
        list[UserResponse]: The updated list of users for the auth role.

    """
    auth_role = auth_role_repository.get_auth_role_by_id(auth_role_id, db)
    validate(
        auth_role,
        EXC_MSG_AUTH_ROLE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    user = user_routes.get_user_by_id(user_id, db)
    validate(
        auth_role not in user.auth_roles,
        EXC_MSG_EMPLOYEE_IS_MEMBER,
        status.HTTP_409_CONFLICT,
    )

    auth_role = auth_role_repository.create_membership(
        auth_role_id, user_id, db
    )
    log_args = {"auth_role_name": auth_role.name, "user_id": user_id}
    create_event_log(MEMBERSHIP_IDENTIFIER, "CREATE", log_args, caller_id, db)
    return auth_role.users


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[AuthRoleExtended],
)
def get_auth_roles(
    db: Session = Depends(get_db),
    user_id: int = Security(requires_permission, scopes=["auth_role.read"]),
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
def get_auth_role_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(requires_permission, scopes=["auth_role.read"]),
):
    """Retrieve data for auth role with provided id.

    Args:
        id (int): Auth role's unique identifier.
        db (Session): Database session for current request.

    Returns:
        AuthRoleExtended: The retrieved auth role.

    """
    auth_role = auth_role_repository.get_auth_role_by_id(id, db)
    validate(
        auth_role,
        EXC_MSG_AUTH_ROLE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return auth_role


@router.get(
    "/{id}/users",
    status_code=status.HTTP_200_OK,
    response_model=list[UserResponse],
)
def get_users_by_auth_role(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["auth_role.read", "employee.read"]
    ),
):
    """Retrieve all users with a given auth role.

    Args:
        id (int): Auth role's unique identifier.
        db (Session): Database session for current request.

    Returns:
        list[UserResponse]: The retrieved users for the given auth role.

    """
    auth_role = get_auth_role_by_id(id, db)
    validate(
        auth_role,
        EXC_MSG_AUTH_ROLE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return auth_role.users


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=AuthRoleExtended,
)
def update_auth_role(
    id: int,
    request: AuthRoleExtended,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["auth_role.update"]
    ),
):
    """Update auth role with provided id.

    Args:
        id (int): Auth role's unique identifier.
        request (AuthRoleExtended): Request data to update auth role.
        db (Session): Database session for current request.

    Returns:
        AuthRoleExtended: The updated auth role.

    """
    validate(
        request.id == id,
        EXC_MSG_IDS_DO_NOT_MATCH,
        status.HTTP_400_BAD_REQUEST,
    )

    auth_role = auth_role_repository.get_auth_role_by_id(id, db)
    validate(
        auth_role,
        EXC_MSG_AUTH_ROLE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    dulicate_auth_role = auth_role_repository.get_auth_role_by_name(
        request.name, db
    )
    validate(
        dulicate_auth_role is None or dulicate_auth_role.id == id,
        EXC_MSG_NAME_ALREADY_EXISTS,
        status.HTTP_409_CONFLICT,
    )

    auth_role = auth_role_repository.update_auth_role(auth_role, request, db)
    log_args = {"auth_role_name": auth_role.name}
    create_event_log(IDENTIFIER, "UPDATE", log_args, caller_id, db)
    return auth_role


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_auth_role(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["auth_role.delete"]
    ),
):
    """Delete auth role with provided id.

    Args:
        id (int): Auth role's unique identifier.
        db (Session): Database session for current request.

    """
    auth_role = auth_role_repository.get_auth_role_by_id(id, db)
    validate(
        auth_role,
        EXC_MSG_AUTH_ROLE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )
    validate(
        len(auth_role.users) == 0,
        EXC_MSG_EMPLOYEES_ASSIGNED,
        status.HTTP_409_CONFLICT,
    )

    auth_role_repository.delete_auth_role(auth_role, db)
    log_args = {"auth_role_name": auth_role.name}
    create_event_log(IDENTIFIER, "DELETE", log_args, caller_id, db)


@router.delete(
    "/{auth_role_id}/users/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=list[UserResponse],
)
def delete_auth_role_membership(
    auth_role_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["auth_role.unassign", "employee.read"]
    ),
):
    """Delete membership.

    Args:
        auth_role_id (int): Auth role in the membership.
        user_id (int): User in the membership.
        db (Session): Database session for current request.

    Returns:
        list[EmployeeBase]: The updated list of users for the auth role.

    """
    auth_role = auth_role_repository.get_auth_role_by_id(auth_role_id, db)
    validate(
        auth_role,
        EXC_MSG_AUTH_ROLE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    user = user_routes.get_user_by_id(user_id, db)
    validate(
        auth_role in user.auth_roles,
        EXC_MSG_EMPLOYEE_NOT_MEMBER,
        status.HTTP_404_NOT_FOUND,
    )

    auth_role = auth_role_repository.delete_membership(
        auth_role_id, user_id, db
    )
    log_args = {"auth_role_name": auth_role.name, "user_id": user_id}
    create_event_log(MEMBERSHIP_IDENTIFIER, "DELETE", log_args, caller_id, db)
    return auth_role.users
