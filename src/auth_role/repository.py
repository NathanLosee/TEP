"""Module providing database interactivity for auth role-related operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.auth_role.models import (
    AuthRolePermission,
    AuthRole,
    AuthRoleMembership,
)
from src.auth_role.schemas import AuthRoleBase, AuthRoleExtended


def create_auth_role(request: AuthRoleBase, db: Session) -> AuthRole:
    """Insert new auth role data.

    Args:
        request (AuthRoleBase): Request data for new auth role.
        db (Session): Database session for the current request.

    Returns:
        Org_unit: The created auth.

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
    auth_role_id: int, employee_id: int, db: Session
) -> AuthRole:
    """Insert new membership data.

    Args:
        auth_role_id (int): The id of the auth role in the membership.
        employee_id (int): The id of the employee in the membership.
        db (Session): Database session for the current request.

    Returns:
        AuthRole: The auth role with updated membership.

    """
    membership = AuthRoleMembership(
        auth_role_id=auth_role_id, employee_id=employee_id
    )
    db.add(membership)
    db.commit()
    auth_role = get_auth_role_by_id(auth_role_id, db)
    db.refresh(auth_role)
    return auth_role


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
        id (int): The id of the auth role to look for.
        db (Session): Database session for the current request.

    Returns:
        (AuthRole | None): The auth role with the provided id, or None if
            not found.

    """
    return db.get(AuthRole, id)


def get_auth_role_by_name(name: str, db: Session) -> AuthRole | None:
    """Retrieve an auth role by a provided name.

    Args:
        name (str): The name of the auth role to look for.
        db (Session): Database session for the current request.

    Returns:
        (AuthRole | None): The auth role with the provided name, or None if
            not found.

    """
    return db.scalars(select(AuthRole).where(AuthRole.name == name)).first()


def update_auth_role(
    auth_role: AuthRole, request: AuthRoleExtended, db: Session
) -> AuthRole:
    """Update an auth's existing data.

    Args:
        auth (Auth): The auth data to be updated.
        request (AuthRoleExtended): Request data for updating auth.
        db (Session): Database session for the current request.

    Returns:
        Auth: The updated auth.
    """
    auth_role_update = AuthRole(
        **request.model_dump(exclude={"permissions"}),
        permissions=[
            AuthRolePermission(**p.model_dump(), auth_role_id=auth_role.id)
            for p in request.permissions
        ],
    )
    db.merge(auth_role_update)
    db.commit()
    db.refresh(auth_role)
    return auth_role


def delete_auth_role(auth_role: AuthRole, db: Session):
    """Delete an auth's data.

    Args:
        auth_role (AuthRole): The auth role data to be deleted.
        db (Session): Database session for the current request.

    """
    db.delete(auth_role)
    db.commit()


def delete_membership(
    auth_role_id: int, employee_id: int, db: Session
) -> AuthRole:
    """Delete a membership's data.

    Args:
        auth_role_id (int): The id of the auth role in the membership.
        employee_id (int): The id of the employee in the membership.
        db (Session): Database session for the current request.

    Returns:
        Auth: The auth role with updated membership.

    """
    membership = db.scalars(
        select(AuthRoleMembership).where(
            AuthRoleMembership.auth_role_id == auth_role_id,
            AuthRoleMembership.employee_id == employee_id,
        )
    ).first()
    db.delete(membership)
    db.commit()
    auth_role = get_auth_role_by_id(auth_role_id, db)
    db.refresh(auth_role)
    return auth_role
