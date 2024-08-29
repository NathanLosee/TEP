from fastapi import status
from fastapi.testclient import TestClient
from src.constants import EXCEPTION_MESSAGE_IDS_DO_NOT_MATCH
from src.encounter.constants import (
    BASE_URL,
    EXCEPTION_MESSAGE_ENCOUNTER_NOT_FOUND,
    EXCEPTION_MESSAGE_ENCOUNTER_NOT_FOR_PATIENT,
)
from src.encounter.schemas import EncounterBase, EncounterBaseWithId
from src.patient.constants import EXCEPTION_MESSAGE_PATIENT_NOT_FOUND
from src.patient.schemas import PatientBase
from tests.conftest import create_patient_id, create_encounter_id


def test_create_encounter_201(
    patient_base: PatientBase,
    encounter_base: EncounterBase,
    encounter_base_with_id: EncounterBaseWithId,
    test_client: TestClient,
):
    patient_id = create_patient_id(patient_base, test_client)
    encounter_base.patient_id = patient_id

    response = test_client.post(
        url=BASE_URL.format(patient_id=patient_id),
        json=encounter_base.model_dump(),
    )
    print(encounter_base.model_dump())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == encounter_base_with_id.model_dump(by_alias=True)


def test_create_encounter_400_patient_ids_not_match(
    patient_base: PatientBase,
    encounter_base: EncounterBase,
    test_client: TestClient,
):
    patient_id = create_patient_id(patient_base, test_client)
    encounter_base.patient_id = patient_id + 1

    response = test_client.post(
        url=BASE_URL.format(patient_id=patient_id),
        json=encounter_base.model_dump(),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == EXCEPTION_MESSAGE_IDS_DO_NOT_MATCH


def test_create_encounter_404_patient_not_exist(
    encounter_base: EncounterBase,
    test_client: TestClient,
):
    patient_id = 1

    response = test_client.post(
        url=BASE_URL.format(patient_id=patient_id),
        json=encounter_base.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXCEPTION_MESSAGE_PATIENT_NOT_FOUND


def test_get_encounters_200_empty_list(
    patient_base: PatientBase,
    test_client: TestClient,
):
    patient_id = create_patient_id(patient_base, test_client)

    response = test_client.get(url=BASE_URL.format(patient_id=patient_id))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_encounters_200_nonempty_list(
    patient_base: PatientBase,
    encounter_base: EncounterBase,
    encounter_base_with_id: EncounterBaseWithId,
    test_client: TestClient,
):
    patient_id = create_patient_id(patient_base, test_client)
    test_client.post(
        url=BASE_URL.format(patient_id=patient_id),
        json=encounter_base.model_dump(),
    )

    response = test_client.get(url=BASE_URL.format(patient_id=patient_id))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        encounter_base_with_id.model_dump(by_alias=True)
    ]


def test_get_encounters_404_patient_not_exist(
    test_client: TestClient,
):
    patient_id = 1

    response = test_client.get(url=BASE_URL.format(patient_id=patient_id))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXCEPTION_MESSAGE_PATIENT_NOT_FOUND


def test_update_encounter_by_id_200(
    patient_base: PatientBase,
    encounter_base: EncounterBase,
    encounter_base_with_id: EncounterBaseWithId,
    test_client: TestClient,
):
    patient_id = create_patient_id(patient_base, test_client)
    encounter_id = create_encounter_id(patient_id, encounter_base, test_client)
    encounter_base_with_id.id = encounter_id

    encounter_base_with_id.provider = "NewCareProvider"

    response = test_client.put(
        url=f"{BASE_URL.format(patient_id=patient_id)}/{encounter_id}",
        json=encounter_base_with_id.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == encounter_base_with_id.model_dump(by_alias=True)


def test_update_encounter_by_id_400_patient_ids_not_match(
    patient_base: PatientBase,
    encounter_base_with_id: EncounterBaseWithId,
    test_client: TestClient,
):
    patient_id = create_patient_id(patient_base, test_client)
    encounter_base_with_id.patient_id = patient_id + 1
    encounter_id = 1

    response = test_client.put(
        url=f"{BASE_URL.format(patient_id=patient_id)}/{encounter_id}",
        json=encounter_base_with_id.model_dump(),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == EXCEPTION_MESSAGE_IDS_DO_NOT_MATCH


def test_update_encounter_by_id_404_patient_not_exist(
    encounter_base_with_id: EncounterBaseWithId,
    test_client: TestClient,
):
    patient_id = 1
    encounter_id = 1

    response = test_client.put(
        url=f"{BASE_URL.format(patient_id=patient_id)}/{encounter_id}",
        json=encounter_base_with_id.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXCEPTION_MESSAGE_PATIENT_NOT_FOUND


def test_update_encounter_by_id_400_encounter_ids_not_match(
    patient_base: PatientBase,
    encounter_base_with_id: EncounterBaseWithId,
    test_client: TestClient,
):
    patient_id = create_patient_id(patient_base, test_client)
    encounter_base_with_id.id = 1
    encounter_id = 2

    response = test_client.put(
        url=f"{BASE_URL.format(patient_id=patient_id)}/{encounter_id}",
        json=encounter_base_with_id.model_dump(),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == EXCEPTION_MESSAGE_IDS_DO_NOT_MATCH


def test_update_encounter_by_id_404_encounter_not_exist(
    patient_base: PatientBase,
    encounter_base_with_id: EncounterBaseWithId,
    test_client: TestClient,
):
    patient_id = create_patient_id(patient_base, test_client)
    encounter_id = 1

    response = test_client.put(
        url=f"{BASE_URL.format(patient_id=patient_id)}/{encounter_id}",
        json=encounter_base_with_id.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXCEPTION_MESSAGE_ENCOUNTER_NOT_FOUND


def test_update_encounter_by_id_404_encounter_not_for_patient(
    patient_base: PatientBase,
    encounter_base: EncounterBase,
    encounter_base_with_id: EncounterBaseWithId,
    test_client: TestClient,
):
    patient_id = create_patient_id(patient_base, test_client)
    encounter_id = create_encounter_id(patient_id, encounter_base, test_client)
    encounter_base_with_id.id = encounter_id

    patient_base.email = "newemail@catalyte.io"
    patient_id = create_patient_id(patient_base, test_client)
    encounter_base_with_id.patient_id = patient_id

    response = test_client.put(
        url=f"{BASE_URL.format(patient_id=patient_id)}/{encounter_id}",
        json=encounter_base_with_id.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert (
        response.json()["detail"]
        == EXCEPTION_MESSAGE_ENCOUNTER_NOT_FOR_PATIENT
    )
