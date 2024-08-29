"""Module defining API for encounter-related operations."""

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from src.database import get_db
import src.services as common_services
from src.encounter.constants import BASE_URL
import src.encounter.repository as encounter_repository
import src.encounter.services as encounter_services
from src.encounter.schemas import EncounterBase, EncounterBaseWithId
import src.patient.services as patient_services
import src.patient.repository as patient_repository

router = APIRouter(prefix=BASE_URL, tags=["encounter"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=EncounterBaseWithId,
)
def create_encounter(
    patient_id: int, request: EncounterBase, db: Session = Depends(get_db)
) -> EncounterBaseWithId:
    """Insert new encounter for encounter.

    Args:
        patient_id (int): The unique identifier of the patient involved in the
            encounter.
        request (EncounterBase): Request data for new encoutner.
        db (Session): Database session for current request.

    Returns:
        EncounterBaseWithId: Response containing newly created encounter data.

    """
    common_services.validate_ids_match(request.patient_id, patient_id)
    patient = patient_repository.get_patient_by_id(patient_id, db)
    patient_services.validate_patient_exists(patient)

    return encounter_repository.create_encounter(request, db)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[EncounterBaseWithId],
)
def get_encounters(
    patient_id: int, db: Session = Depends(get_db)
) -> list[EncounterBaseWithId]:
    """Retrieve all encounter data for a given patient.

    Args:
        patient_id (int): The unique identifier of the patient involved in the
            encounter.
        db (Session): Database session for current request.

    Returns:
        list[EncounterBaseWithId]: The retrieved encounters.

    """
    patient = patient_repository.get_patient_by_id(patient_id, db)
    patient_services.validate_patient_exists(patient)

    return patient.encounters


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=EncounterBaseWithId,
)
def update_encounter(
    patient_id: int,
    id: int,
    request: EncounterBaseWithId,
    db: Session = Depends(get_db),
) -> EncounterBaseWithId:
    """Update data for encounter with provided id.

    Args:
        patient_id (int): The unique identifier of the patient involved in the
            encounter.
        id (int): The encounter's unique identifier.
        request (EncounterBase): Request data to update encounter.
        db (Session): Database session for current request.

    Returns:
        EncounterBaseWithId: The updated encounter.

    """
    common_services.validate_ids_match(request.patient_id, patient_id)
    patient = patient_repository.get_patient_by_id(patient_id, db)
    patient_services.validate_patient_exists(patient)

    common_services.validate_ids_match(request.id, id)
    encounter = encounter_repository.get_encounter_by_id(id, db)
    encounter_services.validate_encounter_exists(encounter)
    encounter_services.validate_encounter_involves_patient(
        encounter, patient_id
    )

    return encounter_repository.update_encounter(encounter, request, db)
