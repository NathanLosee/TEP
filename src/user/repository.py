"""Module providing database interactivity for employee-related operations."""

from typing import Union
from sqlalchemy import select
from sqlalchemy.orm import Session

import src.services as services
from src.user.models import InvalidatedToken, User
from src.user.schemas import UserBase


def create_user(request: UserBase, db: Session) -> User:
    """Insert new employee data.

    Args:
        request (UserBase): Request data for new user.
        db (Session): Database session for the current request.

    Returns:
        User: The created user.

    """
    user = User(**request.model_dump())
    user.password = services.hash_password(request.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_users(db: Session) -> list[User]:
    """Retrieve all existing users.

    Args:
        db (Session): Database session for the current request.

    Returns:
        list[Employee]: The retrieved users.

    """
    return db.scalars(select(User)).all()


def get_user_by_id(id: int, db: Session) -> Union[User, None]:
    """Retrieve a user by a provided id.

    Args:
        id (int): User's unique identifier.
        db (Session): Database session for the current request.

    Returns:
        (Union[User, None]): The user with the provided id, or None if not
            found.

    """
    return db.get(User, id)


def get_user_by_badge_number(
    badge_number: str, db: Session,
) -> Union[User, None]:
    """Retrieve a user by a provided badge number.

    Args:
        badge_number (str): User's badge number.
        db (Session): Database session for the current request.

    Returns:
        (Union[User, None]): The user with the provided badge number, or None
            if not found.

    """
    return db.scalar(select(User).where(User.badge_number == badge_number))


def update_user(user: User, request: UserBase, db: Session) -> User:
    """Update a user's existing data.

    Args:
        user (User): User data to be updated.
        request (UserBase): Request data for updating user.
        db (Session): Database session for the current request.

    Returns:
        User: The updated user.

    """
    if request.password != user.password:
        user.password = services.hash_password(request.password)
    db.add(user)
    db.commit()
    return user


def delete_user(user: User, db: Session) -> None:
    """Delete provided employee data.

    Args:
        user (User): User data to be deleted.
        db (Session): Database session for the current request.

    """
    db.delete(user)
    db.commit()


def invalidate_token(token: str, db: Session) -> None:
    """Invalidate a token by adding it to the invalidated tokens table.

    Args:
        token (str): The token to be invalidated.
        db (Session): Database session for the current request.

    """
    db.add(InvalidatedToken(token=token))
    db.commit()


def get_invalidated_tokens(db: Session) -> list[str]:
    """Retrieve all invalidated tokens.

    Args:
        db (Session): Database session for the current request.

    Returns:
        list[str]: The retrieved invalidated tokens.

    """
    invalidated_tokens = db.scalars(select(InvalidatedToken)).all()
    return [token.token for token in invalidated_tokens]


def clean_invalidated_tokens(db: Session) -> None:
    """Delete expired invalidated tokens.

    Args:
        db (Session): Database session for the current request.

    """
    tokens = db.scalars(select(InvalidatedToken)).all()
    for token in tokens:
        try:
            services.decode_jwt_token(token.token)
        except services.HTTPException:
            db.delete(token)
    db.commit()
