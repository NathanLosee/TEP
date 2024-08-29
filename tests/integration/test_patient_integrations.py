from fastapi import status
from fastapi.testclient import TestClient
from src.constants import EXCEPTION_MESSAGE_IDS_DO_NOT_MATCH
from src.encounter.schemas import EncounterBase
from src.patient.constants import (
    BASE_URL,
    EXCEPTION_MESSAGE_EMAIL_NOT_UNIQUE,
    EXCEPTION_MESSAGE_PATIENT_NOT_FOUND,
    EXCEPTION_MESSAGE_PATIENT_HAS_ENCOUNTERS,
)
from src.patient.schemas import PatientBase, PatientBaseWithId
from tests.conftest import create_patient_id


def test_create_patient_201(
    patient_base: PatientBase,
    patient_base_with_id: PatientBaseWithId,
    test_client: TestClient,
):
    response = test_client.post(url=BASE_URL, json=patient_base.model_dump())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == patient_base_with_id.model_dump()


def test_create_patient_409_email_not_unique(
    patient_base: PatientBase,
    test_client: TestClient,
):
    test_client.post(url=BASE_URL, json=patient_base.model_dump())

    response = test_client.post(url=BASE_URL, json=patient_base.model_dump())

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXCEPTION_MESSAGE_EMAIL_NOT_UNIQUE


def test_get_patients_200_empty_list(
    test_client: TestClient,
):
    response = test_client.get(url=BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_patients_200_nonempty_list(
    patient_base: PatientBase,
    patient_base_with_id: PatientBaseWithId,
    test_client: TestClient,
):
    create_patient_id(patient_base, test_client)

    response = test_client.get(url=BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [patient_base_with_id.model_dump()]


def test_get_patient_by_id_200(
    patient_base: PatientBase,
    patient_base_with_id: PatientBaseWithId,
    test_client: TestClient,
):
    patient_id = create_patient_id(patient_base, test_client)
    patient_base_with_id.id = patient_id

    response = test_client.get(url=f"{BASE_URL}/{patient_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == patient_base_with_id.model_dump()


def test_get_patient_by_id_404_patient_not_found(
    patient_base_with_id: PatientBaseWithId,
    test_client: TestClient,
):
    patient_id = patient_base_with_id.id

    response = test_client.get(url=f"{BASE_URL}/{patient_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXCEPTION_MESSAGE_PATIENT_NOT_FOUND


def test_update_patient_by_id_200(
    patient_base: PatientBase,
    patient_base_with_id: PatientBaseWithId,
    test_client: TestClient,
):
    patient_id = create_patient_id(patient_base, test_client)
    patient_base_with_id.id = patient_id

    patient_base_with_id.last_name = "newlast"

    response = test_client.put(
        url=f"{BASE_URL}/{patient_id}",
        json=patient_base_with_id.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == patient_base_with_id.model_dump()


def test_update_patient_by_id_400_ids_not_match(
    patient_base_with_id: PatientBaseWithId,
    test_client: TestClient,
):
    patient_id = patient_base_with_id.id + 1

    response = test_client.put(
        url=f"{BASE_URL}/{patient_id}",
        json=patient_base_with_id.model_dump(),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == EXCEPTION_MESSAGE_IDS_DO_NOT_MATCH


def test_update_patient_by_id_404_patient_not_found(
    patient_base_with_id: PatientBaseWithId,
    test_client: TestClient,
):
    patient_id = patient_base_with_id.id

    response = test_client.put(
        url=f"{BASE_URL}/{patient_id}",
        json=patient_base_with_id.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXCEPTION_MESSAGE_PATIENT_NOT_FOUND


def test_update_patient_by_id_409_email_not_unique(
    patient_base: PatientBase,
    patient_base_with_id: PatientBaseWithId,
    test_client: TestClient,
):
    patient_id = create_patient_id(patient_base, test_client)
    patient_base_with_id.id = patient_id

    patient_base.email = "new.email@catalyte.io"
    create_patient_id(patient_base, test_client)

    patient_base_with_id.email = patient_base.email

    response = test_client.put(
        url=f"{BASE_URL}/{patient_id}",
        json=patient_base_with_id.model_dump(),
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXCEPTION_MESSAGE_EMAIL_NOT_UNIQUE


def test_delete_patient_by_id_204(
    patient_base: PatientBase,
    test_client: TestClient,
):
    patient_id = create_patient_id(patient_base, test_client)

    response = test_client.delete(url=f"{BASE_URL}/{patient_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_patient_by_id_404_patient_not_found(test_client: TestClient):
    patient_id = 1

    response = test_client.delete(url=f"{BASE_URL}/{patient_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXCEPTION_MESSAGE_PATIENT_NOT_FOUND


def test_delete_patient_by_id_409_patient_has_encounters(
    patient_base: PatientBase,
    encounter_base: EncounterBase,
    test_client: TestClient,
):
    patient_id = create_patient_id(patient_base, test_client)
    response = test_client.post(
        url=f"{BASE_URL}/{patient_id}/encounters",
        json=encounter_base.model_dump(),
    )

    response = test_client.delete(url=f"{BASE_URL}/{patient_id}")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert (
        response.json()["detail"] == EXCEPTION_MESSAGE_PATIENT_HAS_ENCOUNTERS
    )
