from fastapi import status
from fastapi.testclient import TestClient

from src.org_unit.constants import (
    BASE_URL,
    EXC_MSG_EMPLOYEES_ASSIGNED,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_ORG_NOT_FOUND,
)
from tests.conftest import (
    chosen_org_unit_names,
    create_employee,
    create_org_unit,
    random_string,
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
    assert response.json()["detail"]["message"] == EXC_MSG_NAME_ALREADY_EXISTS


def test_get_org_units_200(
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)

    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert org_unit in response.json()


def test_get_org_unit_by_id_200(
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)

    response = test_client.get(f"{BASE_URL}/{org_unit["id"]}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == org_unit


def test_get_org_unit_by_id_404_not_found(
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
    org_unit = create_org_unit(org_unit_data, test_client)

    response = test_client.get(f"{BASE_URL}/{org_unit["id"]}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_employees_by_org_unit_200_nonempty_list(
    org_unit_data: dict,
    employee_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    response = test_client.get(f"{BASE_URL}/{org_unit["id"]}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [employee]


def test_get_employees_by_org_unit_404_not_found(
    test_client: TestClient,
):
    org_unit_id = 999

    response = test_client.get(f"{BASE_URL}/{org_unit_id}/employees")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_ORG_NOT_FOUND}


def test_update_org_unit_by_id_200(
    org_unit_data: dict,
    test_client: TestClient,
):
    new_name = random_string(10)
    while new_name in chosen_org_unit_names:
        new_name = random_string(10)
    chosen_org_unit_names.append(new_name)

    org_unit = create_org_unit(org_unit_data, test_client)
    org_unit["name"] = new_name

    response = test_client.put(
        f"{BASE_URL}/{org_unit["id"]}",
        json=org_unit,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == org_unit
    assert response.json()["name"] == new_name


def test_update_org_unit_by_id_404_not_found(
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


def test_update_org_unit_by_id_409_name_already_exists(
    org_unit_data: dict,
    test_client: TestClient,
):
    new_name = random_string(10)
    while new_name in chosen_org_unit_names:
        new_name = random_string(10)
    chosen_org_unit_names.append(new_name)

    org_unit = create_org_unit(org_unit_data, test_client)
    org_unit["name"] = new_name
    org_unit_data["name"] = new_name
    create_org_unit(org_unit_data, test_client)

    response = test_client.put(
        f"{BASE_URL}/{org_unit["id"]}",
        json=org_unit,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"]["message"] == EXC_MSG_NAME_ALREADY_EXISTS


def test_delete_org_unit_by_id_200(
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)

    response = test_client.delete(f"{BASE_URL}/{org_unit["id"]}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_org_unit_by_id_404_not_found(
    test_client: TestClient,
):
    org_unit_id = 999

    response = test_client.delete(f"{BASE_URL}/{org_unit_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_ORG_NOT_FOUND}


def test_delete_org_unit_by_id_409_employees_assigned(
    org_unit_data: dict,
    employee_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    create_employee(employee_data, test_client)

    response = test_client.delete(f"{BASE_URL}/{org_unit["id"]}")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"]["message"] == EXC_MSG_EMPLOYEES_ASSIGNED
