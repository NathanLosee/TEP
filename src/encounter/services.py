"""Module providing the business logic for encounter-related operations."""

from fastapi import HTTPException, status
from src.encounter.constants import (
    EXCEPTION_MESSAGE_ENCOUNTER_NOT_FOUND,
    EXCEPTION_MESSAGE_ENCOUNTER_NOT_FOR_PATIENT,
)
from src.encounter.models import Encounter


def validate_encounter_exists(encounter: Encounter | None) -> bool:
    """Return whether the provided encounter exists.

    Args:
        encounter (Encounter): The encounter to validate.
        db (Session): Database session for the current request.

    Raises:
        HTTPException (404): If encounter does not exist.

    Returns:
        bool: True if encounter exists.

    """
    if encounter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXCEPTION_MESSAGE_ENCOUNTER_NOT_FOUND,
        )
    return True


def validate_encounter_involves_patient(
    encounter: Encounter, patient_id: int
) -> bool:
    """Return whether the provided encounter possesses the provided patient_id.

    Args:
        encounter (Encounter): The encounter to validate.
        patient_id (int): The patient id to validate.
        db (Session): Database session for the current request.

    Returns:
        bool: True if the encounter possesses the patient_id.

    """
    if encounter.patient_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXCEPTION_MESSAGE_ENCOUNTER_NOT_FOR_PATIENT,
        )
    return True
