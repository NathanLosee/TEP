"""Module providing the business logic for common operations.

This module defines the service layer for handling CRUD
(Create, Read, Update, Delete) operations on common data.

"""

from fastapi import HTTPException, status
from src.constants import EXC_MSG_IDS_DO_NOT_MATCH


def validate_ids_match(body_id: int, path_id: int) -> bool:
    """Return whether the provided ids match.

    Args:
        body_id (int): Id provided in the request body.
        path_id (int): Id provided in the request path.

    Raises:
        HTTPException (409): If the provided ids do not match.

    Returns:
        bool: True if ids match.

    """
    if body_id != path_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=EXC_MSG_IDS_DO_NOT_MATCH,
        )
    return True
