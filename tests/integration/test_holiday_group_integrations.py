from fastapi import status
from fastapi.testclient import TestClient
from src.holiday_group.constants import (
    BASE_URL,
    EXC_MSG_HOLIDAY_NAME_ALREADY_EXISTS,
    EXC_MSG_HOLIDAY_NOT_FOUND,
    EXC_MSG_HOLIDAY_GROUP_NOT_FOUND,
    EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS,
)
from src.holiday_group.schemas import (
    HolidayBase,
    HolidayGroupBase,
    HolidayGroupExtended,
)
from src.employee.constants import BASE_URL as EMPLOYEE_URL
from src.employee.schemas import EmployeeBase, EmployeeExtended
from src.org_unit.constants import BASE_URL as ORG_UNIT_URL
from src.org_unit.schemas import OrgUnitBase


def test_create_holiday_group_201(
    holiday_group_base: HolidayGroupBase,
    holiday_group_extended: HolidayGroupExtended,
    test_client: TestClient,
):
    response = test_client.post(
        BASE_URL,
        json=holiday_group_base.model_dump(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == holiday_group_extended.model_dump()


def test_create_holiday_group_409_name_already_exists(
    holiday_group_base: HolidayGroupBase,
    test_client: TestClient,
):
    test_client.post(
        BASE_URL,
        json=holiday_group_base.model_dump(),
    )

    response = test_client.post(
        BASE_URL,
        json=holiday_group_base.model_dump(),
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS


def test_create_holiday_201(
    holiday_group_base: HolidayGroupBase,
    holiday_base: HolidayBase,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_group_base.model_dump(),
    ).json()["id"]

    response = test_client.post(
        f"{BASE_URL}/{holiday_group_id}/holidays",
        json=holiday_base.model_dump(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["holidays"][0]["name"] == holiday_base.name


def test_create_holiday_409_name_already_exists(
    holiday_group_base: HolidayGroupBase,
    holiday_base: HolidayBase,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_group_base.model_dump(),
    ).json()["id"]

    test_client.post(
        f"{BASE_URL}/{holiday_group_id}/holidays",
        json=holiday_base.model_dump(),
    )
    response = test_client.post(
        f"{BASE_URL}/{holiday_group_id}/holidays",
        json=holiday_base.model_dump(),
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_NAME_ALREADY_EXISTS


def test_create_holiday_404_holiday_group_not_found(
    holiday_base: HolidayBase, test_client: TestClient
):
    holiday_group_id = 999

    response = test_client.post(
        f"{BASE_URL}/{holiday_group_id}/holidays",
        json=holiday_base.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_GROUP_NOT_FOUND


def test_get_holiday_groups_200_empty_list(
    test_client: TestClient,
):
    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_holiday_groups_200_nonempty_list(
    holiday_group_base: HolidayGroupBase,
    holiday_group_extended: HolidayGroupExtended,
    test_client: TestClient,
):
    test_client.post(
        BASE_URL,
        json=holiday_group_base.model_dump(),
    )

    response = test_client.get(f"{BASE_URL}/group")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [holiday_group_extended.model_dump()]


def test_get_holiday_group_200(
    holiday_group_base: HolidayGroupBase,
    holiday_group_extended: HolidayGroupExtended,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_group_base.model_dump(),
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{holiday_group_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == holiday_group_extended.model_dump()


def test_get_holiday_group_404_holiday_group_not_found(
    test_client: TestClient,
):
    holiday_group_id = 999

    response = test_client.get(f"{BASE_URL}/{holiday_group_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_GROUP_NOT_FOUND


def test_get_holidays_by_group_200_empty_list(
    holiday_group_base: HolidayGroupBase, test_client: TestClient
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_group_base.model_dump(),
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{holiday_group_id}/holidays")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_holidays_by_group_200_nonempty_list(
    holiday_group_base: HolidayGroupBase,
    holiday_base: HolidayBase,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_group_base.model_dump(),
    ).json()["id"]
    test_client.post(
        BASE_URL,
        json=holiday_base.model_dump(),
    )

    response = test_client.get(f"{BASE_URL}/{holiday_group_id}/holidays")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["holidays"][0]["name"] == holiday_base.name


def test_get_holidays_by_group_404_holiday_group_not_found(
    test_client: TestClient,
):
    holiday_group_id = 999

    response = test_client.get(f"{BASE_URL}/{holiday_group_id}/holidays")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_GROUP_NOT_FOUND


def test_get_employees_by_holiday_group_200(
    holiday_group_base: HolidayGroupBase,
    employee_base: EmployeeBase,
    employee_extended: EmployeeExtended,
    org_unit_base: OrgUnitBase,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_group_base.model_dump(),
    ).json()["id"]
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_base.model_dump(),
    ).json()["id"]
    employee_base.org_unit_id = org_unit_id
    employee_extended.org_unit_id = org_unit_id
    test_client.post(
        EMPLOYEE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{holiday_group_id}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [employee_extended.model_dump()]


def test_get_employees_by_holiday_group_404_holiday_group_not_found(
    test_client: TestClient,
):
    holiday_group_id = 999

    response = test_client.get(f"{BASE_URL}/{holiday_group_id}/employees")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_GROUP_NOT_FOUND


def test_update_holiday_group_200(
    holiday_group_base: HolidayGroupBase,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_group_base.model_dump(),
    ).json()["id"]

    holiday_group_base.name = "Updated Holiday Group Name"

    response = test_client.put(
        f"{BASE_URL}/{holiday_group_id}",
        json=holiday_group_base.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Updated Holiday Group Name"


def test_update_holiday_200(
    holiday_group_base: HolidayGroupBase,
    holiday_base: HolidayBase,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_group_base.model_dump(),
    ).json()["id"]
    test_client.post(
        f"{BASE_URL}/{holiday_group_id}/holidays",
        json=holiday_base.model_dump(),
    )

    holiday_base.name = "Updated Holiday Name"

    response = test_client.put(
        f"{BASE_URL}/{holiday_group_id}/holidays",
        json=holiday_base.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Updated Holiday Name"


def test_update_holiday_404_holiday_group_not_found(
    holiday_base: HolidayBase,
    test_client: TestClient,
):
    holiday_group_id = 999

    response = test_client.put(
        f"{BASE_URL}/{holiday_group_id}/holidays",
        json=holiday_base.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_GROUP_NOT_FOUND


def test_update_holiday_404_holiday_not_found(
    holiday_base: HolidayBase,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_base.model_dump(),
    ).json()["id"]

    response = test_client.put(
        f"{BASE_URL}/{holiday_group_id}/holidays",
        json=holiday_base.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_NOT_FOUND


def test_delete_holiday_group_204(
    holiday_group_base: HolidayGroupBase,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_group_base.model_dump(),
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


def test_delete_holiday_204(
    holiday_base: HolidayBase,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_base.model_dump(),
    ).json()["id"]
    test_client.post(
        f"{BASE_URL}/{holiday_group_id}/holidays",
        json=holiday_base.model_dump(),
    )

    response = test_client.delete(
        f"{BASE_URL}/{holiday_group_id}/holidays",
        params={"name": holiday_base.name},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_holiday_404_holiday_not_found(
    holiday_base: HolidayBase,
    test_client: TestClient,
):
    holiday_group_id = test_client.post(
        BASE_URL,
        json=holiday_base.model_dump(),
    ).json()["id"]

    response = test_client.delete(
        f"{BASE_URL}/{holiday_group_id}/holidays",
        params={"name": holiday_base.name},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_HOLIDAY_NOT_FOUND
