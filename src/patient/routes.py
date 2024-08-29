"""Module defining API for patient-related operations."""

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from src.database import get_db
import src.services as common_services
from src.patient.constants import BASE_URL
import src.patient.repository as patient_repository
import src.patient.services as patient_services
from src.patient.schemas import PatientBase, PatientBaseWithId

router = APIRouter(prefix=BASE_URL, tags=["patient"])


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=PatientBaseWithId
)
def create_patient(request: PatientBase, db: Session = Depends(get_db)):
    """Insert new patient data.

    Args:
        request (PatientBase): Request data for new patient.
        db (Session): Database session for current request.

    Returns:
        PatientBaseWithId: Response containing newly created patient data.

    """
    patient_with_same_email = patient_repository.get_patient_by_email(
        request.email, db
    )
    patient_services.validate_patient_email_is_unique(
        patient_with_same_email, None
    )

    return patient_repository.create_patient(request, db)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[PatientBaseWithId],
)
def get_patients(db: Session = Depends(get_db)):
    """Retrieve all patient data.

    Args:
        db (Session): Database session for current request.

    Returns:
        list[PatientBaseWithId]: The retrieved patients.

    """
    return patient_repository.get_patients(db)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=PatientBaseWithId,
)
def get_patient_by_id(id: int, db: Session = Depends(get_db)):
    """Retrieve data for patient with provided id.

    Args:
        id (int): The patient's unique identifier.
        db (Session): Database session for current request.

    Returns:
        PatientBaseWithId: The retrieved patient.

    """
    patient = patient_repository.get_patient_by_id(id, db)
    patient_services.validate_patient_exists(patient)

    return patient


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=PatientBaseWithId,
)
def update_patient_by_id(
    id: int, request: PatientBaseWithId, db: Session = Depends(get_db)
):
    """Update data for patient with provided id.

    Args:
        id (int): The patient's unique identifier.
        request (PatientBase): Request data to update patient.
        db (Session): Database session for current request.

    Returns:
        PatientBaseWithId: The updated patient.

    """
    common_services.validate_ids_match(request.id, id)
    patient = patient_repository.get_patient_by_id(id, db)
    patient_services.validate_patient_exists(patient)

    patient_with_same_email = patient_repository.get_patient_by_email(
        request.email, db
    )
    patient_services.validate_patient_email_is_unique(
        patient_with_same_email, id
    )

    return patient_repository.update_patient_by_id(patient, request, db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient_by_id(id: int, db: Session = Depends(get_db)):
    """Delete patient data with provided id.

    Args:
        id (int): The patient's unique identifier.
        db (Session): Database session for current request.

    """
    patient = patient_repository.get_patient_by_id(id, db)
    patient_services.validate_patient_exists(patient)
    patient_services.validate_patient_encounters_list_is_empty(patient)

    patient_repository.delete_patient(patient, db)
