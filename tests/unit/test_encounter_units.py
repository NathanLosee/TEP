from fastapi import HTTPException, status
from pytest import raises
from src.encounter.constants import (
    EXCEPTION_MESSAGE_ENCOUNTER_NOT_FOUND,
    EXCEPTION_MESSAGE_ENCOUNTER_NOT_FOR_PATIENT,
)
from src.encounter.models import Encounter
import src.encounter.services as encounter_services


def test_validate_encounter_exists_success(encounter_model: Encounter):
    assert encounter_services.validate_encounter_exists(encounter_model)


def test_validate_encounter_exists_error_not_found():
    encounter = None

    with raises(HTTPException) as e_info:
        encounter_services.validate_encounter_exists(encounter)

    assert e_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert e_info.value.detail == EXCEPTION_MESSAGE_ENCOUNTER_NOT_FOUND


def test_validate_encounter_involves_patient_success(
    encounter_model: Encounter,
):
    patient_id = 1

    assert encounter_services.validate_encounter_involves_patient(
        encounter_model, patient_id
    )


def test_validate_encounter_involves_patient_error_not_referenced(
    encounter_model: Encounter,
):
    patient_id = 0

    with raises(HTTPException) as e_info:
        encounter_services.validate_encounter_involves_patient(
            encounter_model, patient_id
        )

    assert e_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert e_info.value.detail == EXCEPTION_MESSAGE_ENCOUNTER_NOT_FOR_PATIENT
