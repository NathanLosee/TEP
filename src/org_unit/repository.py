"""Module providing database interactivity for org unit-related operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.org_unit.models import OrgUnit
from src.org_unit.schemas import OrgUnitBase, OrgUnitExtended


def create_org_unit(request: OrgUnitBase, db: Session) -> OrgUnit:
    """Insert new org unit data.

    Args:
        request (OrgUnitBase): Request data for new org unit.
        db (Session): Database session for the current request.

    Returns:
        Org_unit: The created org unit.

    """
    org_unit = OrgUnit(**request.model_dump())
    db.add(org_unit)
    db.commit()
    db.refresh(org_unit)
    return org_unit


def get_org_units(db: Session) -> list[OrgUnit]:
    """Retrieve all org unit data.

    Args:
        db (Session): Database session for the current request.

    Returns:
        list[OrgUnit]: The retrieved org units.

    """
    return db.scalars(select(OrgUnit)).all()


def get_org_unit_by_id(id: int, db: Session) -> OrgUnit | None:
    """Retrieve an org unit by a provided id.

    Args:
        id (int): Org unit's unique identifier.
        db (Session): Database session for the current request.

    Returns:
        (OrgUnit | None): The org unit with the provided id, or None if
            not found.

    """
    return db.get(OrgUnit, id)


def get_org_unit_by_name(name: str, db: Session) -> OrgUnit | None:
    """Retrieve an org unit by a provided name.

    Args:
        name (str): Org unit's name.
        db (Session): Database session for the current request.

    Returns:
        (OrgUnit | None): The org unit with the provided name, or None if
            not found.

    """
    return db.scalars(select(OrgUnit).where(OrgUnit.name == name)).first()


def update_org_unit(
    org_unit: OrgUnit, request: OrgUnitExtended, db: Session
) -> OrgUnit:
    """Update an org unit's existing data.

    Args:
        org_unit (OrgUnit): Org unit data to be updated.
        request (OrgUnitExtended): Request data for updating org unit.
        db (Session): Database session for the current request.

    Returns:
        OrgUnit: The updated org unit.

    """
    org_unit_update = OrgUnit(**request.model_dump())
    db.merge(org_unit_update)
    db.commit()
    db.refresh(org_unit)
    return org_unit


def delete_org_unit(org_unit: OrgUnit, db: Session):
    """Delete an org unit's data.

    Args:
        org_unit (OrgUnit): Org unit data to be deleted.
        db (Session): Database session for the current request.

    """
    db.delete(org_unit)
    db.commit()
