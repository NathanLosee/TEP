"""Module providing the business logic for org unit-related operations."""

from typing import Optional
from fastapi import HTTPException, status
from src.org_unit.constants import (
    EXC_MSG_ORG_NOT_FOUND,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_EMPLOYEES_ASSIGNED,
)
from src.org_unit.models import OrgUnit


def validate_org_unit_exists(org_unit: OrgUnit | None) -> bool:
    """Return whether the provided org unit exists.

    Args:
        org_unit (OrgUnit): The org unit to validate.

    Raises:
        HTTPException (404): If org unit does not exist.

    Returns:
        bool: True if org unit exists.

    """
    if org_unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXC_MSG_ORG_NOT_FOUND,
        )
    return True


def validate_org_unit_name_is_unique(
    org_unit_with_same_name: OrgUnit, update_org_unit_id: Optional[int]
) -> bool:
    """Return whether the provided org unit name is unique.

    Args:
        org_unit_with_same_name (OrgUnit): The org unit that has the same name
            provided in the request.
        update_org_unit_id (Optional[int]): Unique identifier of the org unit
            being updated. Allows org unit to keep same name.

    Raises:
        HTTPException (409): If the provided name is already in use.

    Returns:
        bool: True if org unit name is unique.

    """
    if (
        org_unit_with_same_name is not None
        and org_unit_with_same_name.id != update_org_unit_id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=EXC_MSG_NAME_ALREADY_EXISTS,
        )
    return True


def validate_org_unit_employees_list_is_empty(
    org_unit: OrgUnit | None,
) -> bool:
    """Return whether the provided org unit has employees.

    Args:
        org_unit (OrgUnit): The org unit to validate.

    Raises:
        HTTPException (409): If org unit does have employees.

    Returns:
        bool: True if org unit does not have employees.

    """
    if org_unit.employees is not None and len(org_unit.employees) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=EXC_MSG_EMPLOYEES_ASSIGNED,
        )
    return True
