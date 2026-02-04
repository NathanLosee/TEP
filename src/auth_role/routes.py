"""Module defining API for auth role-related operations."""

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

from src.auth_role.constants import (
    BASE_URL,
    EXC_MSG_AUTH_ROLE_NOT_FOUND,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_USER_IS_MEMBER,
    EXC_MSG_USER_NOT_MEMBER,
    EXC_MSG_USERS_ASSIGNED,
    IDENTIFIER,
    MEMBERSHIP_IDENTIFIER,
)
from src.auth_role.repository import (
    create_auth_role as create_auth_role_in_db,
    create_membership,
    delete_auth_role as delete_auth_role_from_db,
    delete_membership,
    get_auth_role_by_id as get_auth_role_by_id_from_db,
    get_auth_role_by_name,
    get_auth_roles as get_auth_roles_from_db,
    update_auth_role as update_auth_role_in_db,
)
from src.auth_role.schemas import AuthRoleBase, AuthRoleExtended
from src.constants import EXC_MSG_IDS_DO_NOT_MATCH
from src.database import get_db
from src.services import (
    create_event_log,
    requires_license,
    requires_permission,
    validate,
)
from src.user.constants import EXC_MSG_USER_NOT_FOUND
from src.user.repository import get_user_by_id as get_user_by_id_from_db
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
    caller_badge: str = Security(
        requires_permission, scopes=["auth_role.create"]
    ),
    _: None = Depends(requires_license),
):
    """Insert new auth role.

    Args:
        request (AuthRoleBase): Request data for new auth role.
        db (Session): Database session for current request.

    Returns:
        AuthRoleExtended: The created auth role.

    """
    duplicate_auth_role = get_auth_role_by_name(request.name, db)
    validate(
        duplicate_auth_role is None,
        EXC_MSG_NAME_ALREADY_EXISTS,
        status.HTTP_409_CONFLICT,
        field="name",
        constraint="unique",
    )

    auth_role = create_auth_role_in_db(request, db)
    log_args = {"auth_role_name": auth_role.name}
    create_event_log(IDENTIFIER, "CREATE", log_args, caller_badge, db)
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
    caller_badge: str = Security(
        requires_permission, scopes=["auth_role.assign", "user.read"]
    ),
    _: None = Depends(requires_license),
):
    """Insert new membership.

    Args:
        auth_role_id (int): Auth role in the membership.
        user_id (int): User in the membership.
        db (Session): Database session for current request.

    Returns:
        list[UserResponse]: The updated list of users for the auth role.

    """
    auth_role = get_auth_role_by_id_from_db(auth_role_id, db)
    validate(
        auth_role,
        EXC_MSG_AUTH_ROLE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    user = get_user_by_id_from_db(user_id, db)
    validate(
        user,
        EXC_MSG_USER_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )
    validate(
        user not in auth_role.users,
        EXC_MSG_USER_IS_MEMBER,
        status.HTTP_409_CONFLICT,
        field="user_id",
        constraint="membership",
    )

    auth_role = create_membership(auth_role_id, user_id, db)
    log_args = {"auth_role_name": auth_role.name, "user_id": user.badge_number}
    create_event_log(
        MEMBERSHIP_IDENTIFIER, "CREATE", log_args, caller_badge, db
    )
    return auth_role.users


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[AuthRoleExtended],
)
def get_auth_roles(
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["auth_role.read"]
    ),
):
    """Retrieve all auth roles.

    Args:
        db (Session): Database session for current request.
        caller_badge (str): Badge number of authenticated user.

    Returns:
        list[AuthRoleExtended]: The retrieved auth roles.

    """
    return get_auth_roles_from_db(db)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=AuthRoleExtended,
)
def get_auth_role_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["auth_role.read"]
    ),
):
    """Retrieve data for auth role with provided id.

    Args:
        id (int): Auth role's unique identifier.
        db (Session): Database session for current request.

    Returns:
        AuthRoleExtended: The retrieved auth role.

    """
    auth_role = get_auth_role_by_id_from_db(id, db)
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
    caller_badge: str = Security(
        requires_permission, scopes=["auth_role.read", "user.read"]
    ),
):
    """Retrieve all users with a given auth role.

    Args:
        id (int): Auth role's unique identifier.
        db (Session): Database session for current request.

    Returns:
        list[UserResponse]: The retrieved users for the given auth role.

    """
    auth_role = get_auth_role_by_id_from_db(id, db)
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
    caller_badge: str = Security(
        requires_permission, scopes=["auth_role.update"]
    ),
    _: None = Depends(requires_license),
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

    auth_role = get_auth_role_by_id_from_db(id, db)
    validate(
        auth_role,
        EXC_MSG_AUTH_ROLE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    duplicate_auth_role = get_auth_role_by_name(request.name, db)
    validate(
        duplicate_auth_role is None or duplicate_auth_role.id == id,
        EXC_MSG_NAME_ALREADY_EXISTS,
        status.HTTP_409_CONFLICT,
        field="name",
        constraint="unique",
    )

    auth_role = update_auth_role_in_db(auth_role, request, db)
    log_args = {"auth_role_name": auth_role.name}
    create_event_log(IDENTIFIER, "UPDATE", log_args, caller_badge, db)
    return auth_role


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_auth_role(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["auth_role.delete"]
    ),
    _: None = Depends(requires_license),
):
    """Delete auth role with provided id.

    Args:
        id (int): Auth role's unique identifier.
        db (Session): Database session for current request.

    """
    auth_role = get_auth_role_by_id_from_db(id, db)
    validate(
        auth_role,
        EXC_MSG_AUTH_ROLE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )
    validate(
        len(auth_role.users) == 0,
        EXC_MSG_USERS_ASSIGNED,
        status.HTTP_409_CONFLICT,
        constraint="foreign_key",
    )

    delete_auth_role_from_db(auth_role, db)
    log_args = {"auth_role_name": auth_role.name}
    create_event_log(IDENTIFIER, "DELETE", log_args, caller_badge, db)


@router.delete(
    "/{auth_role_id}/users/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=list[UserResponse],
)
def delete_auth_role_membership(
    auth_role_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["auth_role.unassign", "user.read"]
    ),
    _: None = Depends(requires_license),
):
    """Delete membership.

    Args:
        auth_role_id (int): Auth role in the membership.
        user_id (int): User in the membership.
        db (Session): Database session for current request.

    Returns:
        list[UserResponse]: The updated list of users for the auth role.

    """
    auth_role = get_auth_role_by_id_from_db(auth_role_id, db)
    validate(
        auth_role,
        EXC_MSG_AUTH_ROLE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    user = get_user_by_id_from_db(user_id, db)
    validate(
        user,
        EXC_MSG_USER_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )
    validate(
        user in auth_role.users,
        EXC_MSG_USER_NOT_MEMBER,
        status.HTTP_404_NOT_FOUND,
    )

    auth_role = delete_membership(auth_role_id, user_id, db)
    log_args = {"auth_role_name": auth_role.name, "user_id": user.badge_number}
    create_event_log(
        MEMBERSHIP_IDENTIFIER, "DELETE", log_args, caller_badge, db
    )
    return auth_role.users
