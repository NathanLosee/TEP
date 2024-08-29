"""Module providing database interactivity for encounter-related operations."""

from sqlalchemy.orm import Session
from src.encounter.models import Encounter
from src.encounter.schemas import EncounterBase, EncounterBaseWithId


def create_encounter(request: EncounterBase, db: Session) -> Encounter:
    """Insert new encounter data.

    Args:
        request (EncounterBase): Request data for new encounter.
        db (Session): Database session for the current request.

    Returns:
        Encounter: The created encounter.

    """
    encounter = Encounter(**request.model_dump())
    db.add(encounter)
    db.commit()
    db.refresh(encounter)
    return encounter


def get_encounter_by_id(id: int, db: Session) -> Encounter | None:
    """Retrieve a encounter by a provided id.

    Args:
        id (int): The id of the encounter to look for.
        db (Session): Database session for the current request.

    Returns:
        (Encounter | None): The encounter with the provided id, or None if not
            found.

    """
    return db.get(Encounter, id)


def update_encounter(
    encounter: Encounter, request: EncounterBaseWithId, db: Session
) -> Encounter:
    """Update a encounter's existing data.

    Args:
        encounter (Encounter): The encounter data to be updated.
        request (EncounterBaseWithId): Request data for updating encounter.
        db (Session): Database session for the current request.

    Returns:
        Encounter: The updated encounter.

    """
    encounter_update = Encounter(**request.model_dump())
    db.merge(encounter_update)
    db.commit()
    db.refresh(encounter)
    return encounter
