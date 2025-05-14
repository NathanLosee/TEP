from fastapi import status
from fastapi.testclient import TestClient
from src.employee.constants import BASE_URL as EMPLOYEE_URL
from src.org_unit.constants import (
    BASE_URL,
    EXC_MSG_ORG_NOT_FOUND,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_EMPLOYEES_ASSIGNED,
)


def test_create_org_unit_201(
    org_unit_data: dict,
    test_client: TestClient,
):
    response = test_client.post(
        BASE_URL,
        json=org_unit_data,
    )

    org_unit_data["id"] = response.json()["id"]

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == org_unit_data


def test_create_org_unit_409_name_already_exists(
    org_unit_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=org_unit_data)

    response = test_client.post(
        BASE_URL,
        json=org_unit_data,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": EXC_MSG_NAME_ALREADY_EXISTS}


def test_get_org_units_200_nonempty_list(
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        BASE_URL,
        json=org_unit_data,
    ).json()["id"]
    org_unit_data["id"] = org_unit_id

    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert org_unit_data in response.json()


def test_get_org_unit_200(
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(BASE_URL, json=org_unit_data).json()["id"]
    org_unit_data["id"] = org_unit_id

    response = test_client.get(f"{BASE_URL}/{org_unit_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == org_unit_data


def test_get_org_unit_404_not_found(
    test_client: TestClient,
):
    org_unit_id = 999

    response = test_client.get(f"{BASE_URL}/{org_unit_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_ORG_NOT_FOUND}


def test_get_employees_by_org_unit_200_empty_list(
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(BASE_URL, json=org_unit_data).json()["id"]

    response = test_client.get(f"{BASE_URL}/{org_unit_id}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_employees_by_org_unit_200_nonempty_list(
    org_unit_data: dict,
    employee_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        BASE_URL,
        json=org_unit_data,
    ).json()["id"]
    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]
    employee_data["id"] = employee_id

    response = test_client.get(f"{BASE_URL}/{org_unit_id}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [employee_data]


def test_get_employees_by_org_unit_404_not_found(
    test_client: TestClient,
):
    org_unit_id = 999

    response = test_client.get(f"{BASE_URL}/{org_unit_id}/employees")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_ORG_NOT_FOUND}


def test_update_org_unit_200(
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(BASE_URL, json=org_unit_data).json()["id"]
    org_unit_data["name"] = "Updated Org Unit Name"
    org_unit_data["id"] = org_unit_id

    response = test_client.put(
        f"{BASE_URL}/{org_unit_id}",
        json=org_unit_data,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == org_unit_data


def test_update_org_unit_404_not_found(
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = 999
    org_unit_data["id"] = org_unit_id

    response = test_client.put(
        f"{BASE_URL}/{org_unit_id}",
        json=org_unit_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_ORG_NOT_FOUND}


def test_update_org_unit_409_name_already_exists(
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(BASE_URL, json=org_unit_data).json()["id"]
    org_unit_data["id"] = org_unit_id
    org_unit_data["name"] = "Updated Org Unit Name"
    test_client.post(BASE_URL, json=org_unit_data)

    response = test_client.put(
        f"{BASE_URL}/{org_unit_id}",
        json=org_unit_data,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": EXC_MSG_NAME_ALREADY_EXISTS}


def test_delete_org_unit_200(
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(BASE_URL, json=org_unit_data).json()["id"]

    response = test_client.delete(f"{BASE_URL}/{org_unit_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_org_unit_404_not_found(
    test_client: TestClient,
):
    org_unit_id = 999

    response = test_client.delete(f"{BASE_URL}/{org_unit_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_ORG_NOT_FOUND}


def test_delete_org_unit_409_employees_assigned(
    org_unit_data: dict,
    employee_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(BASE_URL, json=org_unit_data).json()["id"]
    employee_data["org_unit_id"] = org_unit_id
    test_client.post(EMPLOYEE_URL, json=employee_data)

    response = test_client.delete(f"{BASE_URL}/{org_unit_id}")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": EXC_MSG_EMPLOYEES_ASSIGNED}
