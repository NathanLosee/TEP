"""Module providing the business logic for patient-related operations."""

from typing import Optional
from fastapi import HTTPException, status
from src.patient.constants import (
    EXCEPTION_MESSAGE_EMAIL_NOT_UNIQUE,
    EXCEPTION_MESSAGE_PATIENT_NOT_FOUND,
    EXCEPTION_MESSAGE_PATIENT_HAS_ENCOUNTERS,
)
from src.patient.models import Patient


def validate_patient_email_is_unique(
    patient_with_same_email: Patient, update_patient_id: Optional[int]
) -> bool:
    """Return whether the provided patient email is unique.

    Args:
        patient_with_same_email (Patient): The patient that has the same email
            provided in the request.
        update_patient_id (Optional[int]): Unique identifier of the patient
            being updated. Allows patient to keep same email.
        db (Session): Database session for the current request.

    Raises:
        HTTPException (409): If the provided email is already in use.

    Returns:
        bool: True if patient email is unique.

    """
    if (
        patient_with_same_email is not None
        and patient_with_same_email.id != update_patient_id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=EXCEPTION_MESSAGE_EMAIL_NOT_UNIQUE,
        )
    return True


def validate_patient_exists(patient: Patient | None) -> bool:
    """Return whether the provided patient exists.

    Args:
        patient (Patient): The patient to validate.
        db (Session): Database session for the current request.

    Raises:
        HTTPException (404): If patient does not exist.

    Returns:
        bool: True if patient exists.

    """
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXCEPTION_MESSAGE_PATIENT_NOT_FOUND,
        )
    return True


def validate_patient_encounters_list_is_empty(patient: Patient | None) -> bool:
    """Return whether the provided patient has encounters.

    Args:
        patient (Patient): The patient to validate.
        db (Session): Database session for the current request.

    Raises:
        HTTPException (409): If patient does has encounters.

    Returns:
        bool: True if patient does not have encounters.

    """
    if patient.encounters is not None and len(patient.encounters) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=EXCEPTION_MESSAGE_PATIENT_HAS_ENCOUNTERS,
        )
    return True
