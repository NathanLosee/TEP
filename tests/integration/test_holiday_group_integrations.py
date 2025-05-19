from fastapi import status
from fastapi.testclient import TestClient

from src.employee.constants import BASE_URL as EMPLOYEE_URL
from src.holiday_group.constants import (
    BASE_URL,
    EXC_MSG_DUPLICATE_HOLIDAY_NAME,
    EXC_MSG_END_DATE_BEFORE_START_DATE,
    EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS,
    EXC_MSG_HOLIDAY_GROUP_NOT_FOUND,
)
from src.org_unit.constants import BASE_URL as ORG_UNIT_URL


def test_create_holiday_group_201(
    holiday_group_data: dict,
    test_client: TestClient,
):
    response = test_client.post(
        BASE_URL,
        json=holiday_group_data,
    )

    holiday_group_data["id"] = response.json()["id"]

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == holiday_group_data


def test_create_holiday_group_400_end_date_before_start_date(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group_data["holidays"][0]["end_date"] = "2023-01-01"
    holiday_group_data["holidays"][0]["start_date"] = "2023-01-02"
    response = test_client.post(
        BASE_URL,
        json=holiday_group_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == EXC_MSG_END_DATE_BEFORE_START_DATE


def test_create_holiday_group_400_duplicate_holiday_name(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group_data["holidays"].append(
        {
            "name": holiday_group_data["holidays"][0]["name"],
            "start_date": "2023-01-01",
            "end_date": "2023-01-02",
        }
    )
    response = test_client.post(
        BASE_URL,
        json=holiday_group_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == EXC_MSG_DUPLICATE_HOLIDAY_NAME


def test_create_holiday_group_409_name_already_exists(
    holiday_group_data: dict,
    test_client: TestClient,
):
    test_client.post(
        BASE_URL,
        json=holiday_group_data,
    )

    response = test_client.post(
        BASE_URL,
        json=holiday_group_data,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS


def test_get_holiday_groups_200_empty_list(
    test_client: TestClient,
):
    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_holiday_groups_200_nonempty_list(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_group_data,
    ).json()["id"]

    response = test_client.get(BASE_URL)

    holiday_group_data["id"] = holiday_group_id
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [holiday_group_data]


def test_get_holiday_group_200(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_group_data,
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{holiday_group_id}")

    holiday_group_data["id"] = holiday_group_id
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == holiday_group_data


def test_get_holiday_group_404_holiday_group_not_found(
    test_client: TestClient,
):
    holiday_group_id = 999

    response = test_client.get(f"{BASE_URL}/{holiday_group_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_GROUP_NOT_FOUND


def test_get_employees_by_holiday_group_200(
    holiday_group_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_group_data,
    ).json()["id"]

    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_data["holiday_group_id"] = holiday_group_id
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{holiday_group_id}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["id"] == employee_id


def test_get_employees_by_holiday_group_404_holiday_group_not_found(
    test_client: TestClient,
):
    holiday_group_id = 999

    response = test_client.get(f"{BASE_URL}/{holiday_group_id}/employees")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_GROUP_NOT_FOUND


def test_update_holiday_group_200(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_group_data,
    ).json()["id"]

    holiday_group_data["id"] = holiday_group_id
    holiday_group_data["name"] = "Updated Holiday Group Name"
    response = test_client.put(
        f"{BASE_URL}/{holiday_group_id}",
        json=holiday_group_data,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == holiday_group_data


def test_update_holiday_group_200_add_holiday(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_group_data,
    ).json()["id"]

    holiday_group_data["id"] = holiday_group_id
    holiday_group_data["holidays"].append(
        {
            "name": "New Holiday",
            "start_date": "2023-12-25",
            "end_date": "2023-12-25",
        }
    )
    response = test_client.put(
        f"{BASE_URL}/{holiday_group_id}",
        json=holiday_group_data,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == holiday_group_data


def test_update_holiday_group_200_remove_holiday(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_group_data,
    ).json()["id"]

    holiday_group_data["id"] = holiday_group_id
    holiday_group_data["holidays"].pop(0)
    response = test_client.put(
        f"{BASE_URL}/{holiday_group_id}",
        json=holiday_group_data,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == holiday_group_data


def test_delete_holiday_group_204(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_group_data,
    ).json()["id"]

    response = test_client.delete(f"{BASE_URL}/{holiday_group_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_holiday_group_404_holiday_group_not_found(
    test_client: TestClient,
):
    holiday_group_id = 999

    response = test_client.delete(f"{BASE_URL}/{holiday_group_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_GROUP_NOT_FOUND
