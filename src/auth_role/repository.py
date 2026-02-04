"""Module providing database interactivity for auth role-related operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.auth_role.models import (
    AuthRole,
    AuthRoleMembership,
    AuthRolePermission,
)
from src.auth_role.schemas import AuthRoleBase, AuthRoleExtended


def create_auth_role(request: AuthRoleBase, db: Session) -> AuthRole:
    """Insert new auth role data.

    Args:
        request (AuthRoleBase): Request data for new auth role.
        db (Session): Database session for the current request.

    Returns:
        AuthRole: The created auth role.

    """
    auth_role = AuthRole(
        **request.model_dump(exclude={"permissions"}),
        permissions=[
            AuthRolePermission(**p.model_dump()) for p in request.permissions
        ],
    )
    db.add(auth_role)
    db.commit()
    return auth_role


def create_membership(
    auth_role_id: int, user_id: int, db: Session
) -> AuthRole:
    """Insert new auth role membership data.

    Args:
        auth_role_id (int): Auth role in the membership.
        user_id (int): User in the membership.
        db (Session): Database session for the current request.

    Returns:
        AuthRole: The auth role with updated membership.

    """
    membership = AuthRoleMembership(auth_role_id=auth_role_id, user_id=user_id)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return get_auth_role_by_id(auth_role_id, db)


def get_auth_roles(db: Session) -> list[AuthRole]:
    """Retrieve all auth role data.

    Args:
        db (Session): Database session for the current request.

    Returns:
        list[Auth]: The retrieved auth roles.

    """
    return db.scalars(select(AuthRole)).all()


def get_auth_role_by_id(id: int, db: Session) -> AuthRole | None:
    """Retrieve an auth role by a provided id.

    Args:
        id (int): Auth role's unique identifier.
        db (Session): Database session for the current request.

    Returns:
        (AuthRole | None): The auth role with the provided id, or None if
            not found.

    """
    return db.get(AuthRole, id)


def get_auth_role_by_name(name: str, db: Session) -> AuthRole | None:
    """Retrieve an auth role by a provided name.

    Args:
        name (str): Auth role's name.
        db (Session): Database session for the current request.

    Returns:
        (AuthRole | None): The auth role with the provided name, or
            None if not found.

    """
    return db.scalars(select(AuthRole).where(AuthRole.name == name)).first()


def update_auth_role(
    auth_role: AuthRole, request: AuthRoleExtended, db: Session
) -> AuthRole:
    """Update an auth's existing data.

    Args:
        auth_role (AuthRole): Auth role data to be updated.
        request (AuthRoleExtended): Request data for updating auth role.
        db (Session): Database session for the current request.

    Returns:
        AuthRole: The updated auth role.

    """
    auth_role.name = request.name

    request_permissions = set(p.resource for p in request.permissions)
    auth_role_permissions = set(p.resource for p in auth_role.permissions)
    added_permissions = request_permissions - auth_role_permissions
    removed_permissions = auth_role_permissions - request_permissions
    for permission in auth_role.permissions:
        if permission.resource in removed_permissions:
            db.delete(permission)
    for permission in request.permissions:
        if permission.resource in added_permissions:
            permission = AuthRolePermission(
                resource=permission.resource, auth_role_id=auth_role.id
            )
            db.add(permission)

    db.add(auth_role)
    db.commit()
    db.refresh(auth_role)
    return auth_role


def delete_auth_role(auth_role: AuthRole, db: Session):
    """Delete an auth's data.

    Args:
        auth_role (AuthRole): Auth role data to be deleted.
        db (Session): Database session for the current request.

    """
    db.delete(auth_role)
    db.commit()


def delete_membership(
    auth_role_id: int, user_id: int, db: Session
) -> AuthRole:
    """Delete a membership's data.

    Args:
        auth_role_id (int): Auth role in the membership.
        user_id (int): User in the membership.
        db (Session): Database session for the current request.

    Returns:
        Auth: The auth role with updated membership.

    """
    membership = db.scalars(
        select(AuthRoleMembership).where(
            AuthRoleMembership.auth_role_id == auth_role_id,
            AuthRoleMembership.user_id == user_id,
        )
    ).first()
    db.delete(membership)
    db.commit()
    return get_auth_role_by_id(auth_role_id, db)
