from fastapi import HTTPException, status
from pytest import raises
from src.patient.constants import (
    EXCEPTION_MESSAGE_STATE_NOT_VALID,
    EXCEPTION_MESSAGE_GENDER_INPUT_NOT_VALID,
    EXCEPTION_MESSAGE_EMAIL_NOT_UNIQUE,
    EXCEPTION_MESSAGE_PATIENT_NOT_FOUND,
    EXCEPTION_MESSAGE_PATIENT_HAS_ENCOUNTERS,
)
from src.patient.models import Patient
from src.patient.schemas import PatientBase
import src.patient.services as patient_services


def test_patient_base_schema_success(patient_data: dict):
    assert PatientBase(**patient_data)


def test_patient_base_schema_error_invalid_state(patient_data: dict):
    patient_data["state"] = "AA"

    with raises(ValueError) as e_info:
        PatientBase(**patient_data)

    assert EXCEPTION_MESSAGE_STATE_NOT_VALID in str(e_info.value)


def test_patient_base_schema_error_invalid_gender_input(patient_data: dict):
    patient_data["gender"] = "amorphous blob"

    with raises(ValueError) as e_info:
        PatientBase(**patient_data)

    assert EXCEPTION_MESSAGE_GENDER_INPUT_NOT_VALID in str(e_info.value)


def test_validate_patient_email_is_unique_success_create():
    patient_with_same_email = None
    update_patient_id = None

    assert patient_services.validate_patient_email_is_unique(
        patient_with_same_email, update_patient_id
    )


def test_validate_patient_email_is_unique_success_update(
    patient_model: Patient,
):
    update_patient_id = 1

    assert patient_services.validate_patient_email_is_unique(
        patient_model, update_patient_id
    )


def test_validate_patient_email_is_unique_error_patient_has_email(
    patient_model: Patient,
):
    update_patient_id = None

    with raises(HTTPException) as e_info:
        patient_services.validate_patient_email_is_unique(
            patient_model, update_patient_id
        )

    assert e_info.value.status_code == status.HTTP_409_CONFLICT
    assert e_info.value.detail == EXCEPTION_MESSAGE_EMAIL_NOT_UNIQUE


def test_validate_patient_email_is_unique_error_other_patient_has_email(
    patient_model: Patient,
):
    update_patient_id = 2

    with raises(HTTPException) as e_info:
        patient_services.validate_patient_email_is_unique(
            patient_model, update_patient_id
        )

    assert e_info.value.status_code == status.HTTP_409_CONFLICT
    assert e_info.value.detail == EXCEPTION_MESSAGE_EMAIL_NOT_UNIQUE


def test_validate_patient_exists_success(patient_model: Patient):
    assert patient_services.validate_patient_exists(patient_model)


def test_validate_patient_exists_error_not_found():
    patient = None

    with raises(HTTPException) as e_info:
        patient_services.validate_patient_exists(patient)

    assert e_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert e_info.value.detail == EXCEPTION_MESSAGE_PATIENT_NOT_FOUND


def test_validate_patient_encounters_list_is_empty_success(
    patient_model: Patient,
):
    patient_model.encounters = []

    assert patient_services.validate_patient_encounters_list_is_empty(
        patient_model
    )


def test_validate_patient_encounters_list_is_empty_error_not_empty(
    patient_model: Patient,
):
    with raises(HTTPException) as e_info:
        patient_services.validate_patient_encounters_list_is_empty(
            patient_model
        )

    assert e_info.value.status_code == status.HTTP_409_CONFLICT
    assert e_info.value.detail == EXCEPTION_MESSAGE_PATIENT_HAS_ENCOUNTERS
