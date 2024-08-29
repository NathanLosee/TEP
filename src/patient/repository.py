"""Module providing database interactivity for patient-related operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.patient.models import Patient
from src.patient.schemas import PatientBase, PatientBaseWithId


def create_patient(request: PatientBase, db: Session) -> Patient:
    """Insert new patient data.

    Args:
        request (PatientBase): Request data for new patient.
        db (Session): Database session for the current request.

    Returns:
        Patient: The created patient.

    """
    patient = Patient(**request.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patients(db: Session) -> list[Patient]:
    """Retrieve all existing patients.

    Args:
        db (Session): Database session for the current request.

    Returns:
        list[Patient]: The retrieved patients.

    """
    return db.scalars(select(Patient)).all()


def get_patient_by_id(id: int, db: Session) -> Patient | None:
    """Retrieve a patient by a provided id.

    Args:
        id (int): The id of the patient to look for.
        db (Session): Database session for the current request.

    Returns:
        (Patient | None): The patient with the provided id, or None if not
            found.

    """
    return db.get(Patient, id)


def get_patient_by_email(email: str, db: Session) -> Patient | None:
    """Retrieve a patient by a provided email.

    Args:
        email (str): The email of the patient to look for.
        db (Session): Database session for the current request.

    Returns:
        (Patient | None): The patient with the provided email, or None if not
            found.

    """
    return db.scalars(select(Patient).where(Patient.email == email)).first()


def update_patient_by_id(
    patient: Patient, request: PatientBaseWithId, db: Session
) -> Patient:
    """Update a patient's existing data.

    Args:
        patient (Patient): The patient data to be updated.
        request (PatientBaseWithId): Request data for updating patient.
        db (Session): Database session for the current request.

    Returns:
        Patient: The updated patient.

    """
    patient_update = Patient(**request.model_dump())
    db.merge(patient_update)
    db.commit()
    db.refresh(patient)
    return patient


def delete_patient(patient: Patient, db: Session) -> None:
    """Delete provided patient data.

    Args:
        patient (Patient): The patient data to be delete.
        db (Session): Database session for the current request.

    """
    db.delete(patient)
    db.commit()
