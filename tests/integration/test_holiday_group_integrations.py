from fastapi import status
from fastapi.testclient import TestClient

from src.holiday_group.constants import (
    BASE_URL,
    EXC_MSG_DUPLICATE_HOLIDAY_NAME,
    EXC_MSG_END_DATE_BEFORE_START_DATE,
    EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS,
    EXC_MSG_HOLIDAY_GROUP_NOT_FOUND,
)
from tests.conftest import (
    chosen_holiday_group_names,
    create_employee,
    create_holiday_group,
    create_org_unit,
    random_string,
)


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
    create_holiday_group(holiday_group_data, test_client)

    response = test_client.post(
        BASE_URL,
        json=holiday_group_data,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS


def test_get_holiday_groups_200(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group = create_holiday_group(holiday_group_data, test_client)

    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert holiday_group in response.json()


def test_get_holiday_group_by_id_200(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group = create_holiday_group(holiday_group_data, test_client)

    response = test_client.get(f"{BASE_URL}/{holiday_group["id"]}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == holiday_group


def test_get_holiday_group_by_id_404_holiday_group_not_found(
    test_client: TestClient,
):
    holiday_group_id = 999

    response = test_client.get(f"{BASE_URL}/{holiday_group_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_GROUP_NOT_FOUND


def test_get_employees_by_holiday_group_200_empty_list(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group = create_holiday_group(holiday_group_data, test_client)

    response = test_client.get(f"{BASE_URL}/{holiday_group["id"]}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_employees_by_holiday_group_200_nonempty_list(
    holiday_group_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    holiday_group = create_holiday_group(holiday_group_data, test_client)
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["holiday_group_id"] = holiday_group["id"]
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    response = test_client.get(f"{BASE_URL}/{holiday_group["id"]}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [employee]


def test_get_employees_by_holiday_group_404_holiday_group_not_found(
    test_client: TestClient,
):
    holiday_group_id = 999

    response = test_client.get(f"{BASE_URL}/{holiday_group_id}/employees")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_GROUP_NOT_FOUND


def test_update_holiday_group_by_id_200(
    holiday_group_data: dict,
    test_client: TestClient,
):
    new_name = random_string(10)
    while new_name in chosen_holiday_group_names:
        new_name = random_string(10)
    chosen_holiday_group_names.append(new_name)

    holiday_group = create_holiday_group(holiday_group_data, test_client)
    holiday_group["name"] = new_name

    response = test_client.put(
        f"{BASE_URL}/{holiday_group["id"]}",
        json=holiday_group,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == holiday_group
    assert response.json()["name"] == new_name


def test_update_holiday_group_by_id_200_add_holiday(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group = create_holiday_group(holiday_group_data, test_client)
    holiday_group["holidays"].append(
        {
            "name": "New Holiday",
            "start_date": "2023-12-25",
            "end_date": "2023-12-25",
        }
    )
    response = test_client.put(
        f"{BASE_URL}/{holiday_group["id"]}",
        json=holiday_group,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == holiday_group
    assert {
        "name": "New Holiday",
        "start_date": "2023-12-25",
        "end_date": "2023-12-25",
    } in response.json()["holidays"]


def test_update_holiday_group_by_id_200_remove_holiday(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group = create_holiday_group(holiday_group_data, test_client)
    holiday_group["holidays"].pop(0)

    response = test_client.put(
        f"{BASE_URL}/{holiday_group["id"]}",
        json=holiday_group,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == holiday_group
    assert response.json()["holidays"] == []


def test_update_holiday_group_by_id_400_end_date_before_start_date(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group = create_holiday_group(holiday_group_data, test_client)
    holiday_group["holidays"][0]["end_date"] = "2023-01-01"
    holiday_group["holidays"][0]["start_date"] = "2023-01-02"

    response = test_client.put(
        f"{BASE_URL}/{holiday_group["id"]}",
        json=holiday_group,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == EXC_MSG_END_DATE_BEFORE_START_DATE


def test_update_holiday_group_by_id_400_duplicate_holiday_name(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group = create_holiday_group(holiday_group_data, test_client)
    holiday_group["holidays"].append(
        {
            "name": holiday_group["holidays"][0]["name"],
            "start_date": "2023-01-01",
            "end_date": "2023-01-02",
        }
    )
    response = test_client.put(
        f"{BASE_URL}/{holiday_group["id"]}",
        json=holiday_group,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == EXC_MSG_DUPLICATE_HOLIDAY_NAME


def test_update_holiday_group_by_id_404_holiday_group_not_found(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group_id = 999
    holiday_group_data["id"] = holiday_group_id

    response = test_client.put(
        f"{BASE_URL}/{holiday_group_id}",
        json=holiday_group_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_GROUP_NOT_FOUND


def test_update_holiday_group_by_id_409_name_already_exists(
    holiday_group_data: dict,
    test_client: TestClient,
):
    new_name = random_string(10)
    while new_name in chosen_holiday_group_names:
        new_name = random_string(10)
    chosen_holiday_group_names.append(new_name)

    holiday_group = create_holiday_group(holiday_group_data, test_client)
    holiday_group["name"] = new_name
    holiday_group_data["name"] = new_name
    create_holiday_group(holiday_group_data, test_client)

    response = test_client.put(
        f"{BASE_URL}/{holiday_group["id"]}",
        json=holiday_group,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS


def test_delete_holiday_group_by_id_204(
    holiday_group_data: dict,
    test_client: TestClient,
):
    holiday_group = create_holiday_group(holiday_group_data, test_client)

    response = test_client.delete(f"{BASE_URL}/{holiday_group["id"]}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_holiday_group_by_id_404_holiday_group_not_found(
    test_client: TestClient,
):
    holiday_group_id = 999

    response = test_client.delete(f"{BASE_URL}/{holiday_group_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_GROUP_NOT_FOUND
