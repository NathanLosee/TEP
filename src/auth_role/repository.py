"""Module providing database interactivity for auth role-related operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.auth_role.models import (
    AuthRolePermission,
    AuthRole,
    AuthRoleMembership,
)
from src.auth_role.schemas import (
    PermissionBase,
    AuthRoleBase,
    AuthRoleExtended,
)
from src.constants import ResourceType, HTTPMethod


def create_auth_role(request: AuthRoleBase, db: Session) -> AuthRole:
    """Insert new auth role data.

    Args:
        request (AuthRoleBase): Request data for new auth role.
        db (Session): Database session for the current request.

    Returns:
        Org_unit: The created auth.

    """
    auth_role = AuthRole(**request.model_dump())
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
        Auth: The auth role with updated membership.

    """
    membership = AuthRoleMembership(
        auth_role_id=auth_role_id, employee_id=employee_id
    )
    db.add(membership)
    db.commit()
    return get_auth_role_by_id(auth_role_id, db)


def create_permission(
    auth_role_id: int, request: PermissionBase, db: Session
) -> AuthRole:
    """Insert new permission data.

    Args:
        auth_role_id (int): The id of the auth role in the permission.
        request (PermissionBase): Request data for new permission.
        db (Session): Database session for the current request.

    Returns:
        Auth: The auth role with updated permissions.

    """
    permission = AuthRolePermission(
        auth_role_id=auth_role_id, **request.model_dump()
    )
    db.add(permission)
    db.commit()
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
        request (AuthExtended): Request data for updating auth.
        db (Session): Database session for the current request.

    Returns:
        Auth: The updated auth.
    """
    auth_role_update = AuthRole(**request.model_dump())
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
    db.delete(
        select(AuthRoleMembership)
        .where(AuthRoleMembership.auth_role_id == auth_role_id)
        .where(AuthRoleMembership.employee_id == employee_id)
    )
    db.commit()
    return get_auth_role_by_id(auth_role_id, db)


def delete_permission(
    auth_role_id: int,
    resource: ResourceType,
    http_method: HTTPMethod,
    db: Session,
) -> AuthRole:
    """Delete a permission's data.

    Args:
        auth_role_id (int): The id of the auth role in the permission.
        resource (ResourceType): The resource of the permission.
        http_method (HTTPMethod): The HTTP method of the permission.
        db (Session): Database session for the current request.

    Returns:
        Auth: The auth role with updated permissions.

    """
    db.delete(
        select(AuthRolePermission)
        .where(AuthRolePermission.auth_role_id == auth_role_id)
        .where(AuthRolePermission.resource == resource)
        .where(AuthRolePermission.http_method == http_method)
    )
    db.commit()
    return get_auth_role_by_id(auth_role_id, db)
