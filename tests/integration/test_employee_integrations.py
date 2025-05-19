from fastapi import status
from fastapi.testclient import TestClient

from src.department.constants import BASE_URL as DEPARTMENT_URL
from src.employee.constants import BASE_URL, EXC_MSG_EMPLOYEE_NOT_FOUND
from src.holiday_group.constants import BASE_URL as HOLIDAY_GROUP_URL
from src.org_unit.constants import BASE_URL as ORG_UNIT_URL
from src.timeclock.constants import BASE_URL as TIMECLOCK_URL
from src.user.constants import BASE_URL as USER_URL


def test_create_employee_201(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    response = test_client.post(
        BASE_URL,
        json=employee_data,
    )

    employee_data["id"] = response.json()["id"]

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == employee_data


def test_get_employees_200_nonempty_list(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_data,
    ).json()["id"]

    response = test_client.get(BASE_URL)

    employee_data["id"] = employee_id
    assert response.status_code == status.HTTP_200_OK
    assert employee_data in response.json()


def test_get_employee_200(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_data,
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{employee_id}")

    employee_data["id"] = employee_id
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == employee_data


def test_get_employee_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.get(f"{BASE_URL}/{employee_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND


def test_get_employee_departments_200(
    employee_data: dict,
    org_unit_data: dict,
    department_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_data,
    ).json()["id"]

    department_id = test_client.post(
        DEPARTMENT_URL,
        json=department_data,
    ).json()["id"]

    test_client.post(
        f"{DEPARTMENT_URL}/{department_id}/employees/{employee_id}",
    )

    response = test_client.get(f"{BASE_URL}/{employee_id}/departments")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [department_data["name"]]


def test_get_employee_departments_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.get(f"{BASE_URL}/{employee_id}/departments")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND


def test_get_employee_org_unit_200(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_data,
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{employee_id}/org_unit")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == org_unit_data["name"]


def test_get_employee_org_unit_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.get(f"{BASE_URL}/{employee_id}/org_unit")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND


def test_get_employee_holiday_group_200(
    employee_data: dict,
    org_unit_data: dict,
    holiday_group_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]

    holiday_group_id = test_client.post(
        HOLIDAY_GROUP_URL,
        json=holiday_group_data,
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_data["holiday_group_id"] = holiday_group_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_data,
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{employee_id}/holiday_group")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == holiday_group_data["name"]


def test_get_employee_holiday_group_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.get(f"{BASE_URL}/{employee_id}/holiday_group")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND


def test_get_employee_manager_200(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_data["first_name"] = "Test"
    employee_data["last_name"] = "Manager"
    manager_id = test_client.post(
        BASE_URL,
        json=employee_data,
    ).json()["id"]

    employee_data["id"] = 3
    employee_data["manager_id"] = manager_id
    employee_data["first_name"] = "Test"
    employee_data["last_name"] = "Employee"
    employee_id = test_client.post(
        BASE_URL,
        json=employee_data,
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{employee_id}/manager")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "first_name": "Test",
        "last_name": "Manager",
    }


def test_get_employee_manager_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.get(f"{BASE_URL}/{employee_id}/manager")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND


def test_update_employee_200(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_data,
    ).json()["id"]

    employee_data["id"] = employee_id
    employee_data["first_name"] = "Updated Employee Name"
    response = test_client.put(
        f"{BASE_URL}/{employee_id}",
        json=employee_data,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["first_name"] == "Updated Employee Name"


def test_update_employee_404_employee_not_found(
    employee_data: dict,
    test_client: TestClient,
):
    employee_id = 999

    employee_data["id"] = employee_id
    response = test_client.put(
        f"{BASE_URL}/{employee_id}",
        json=employee_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND


def test_update_employee_id_200(
    department_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_data,
    ).json()["id"]

    department_id = test_client.post(
        DEPARTMENT_URL,
        json=department_data,
    ).json()["id"]

    test_client.post(
        f"{DEPARTMENT_URL}/{department_id}/employees/{employee_id}",
    )

    test_client.post(f"{TIMECLOCK_URL}/{employee_id}").json()

    new_id = 12
    response = test_client.put(f"{BASE_URL}/{employee_id}/change_id/{new_id}")

    employee_data["id"] = new_id
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == employee_data["id"]


def test_update_employee_id_200_with_user(
    org_unit_data: dict,
    employee_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]

    employee_data["id"] = 0
    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_data,
    ).json()["id"]

    new_id = 12
    response = test_client.put(f"{BASE_URL}/{employee_id}/change_id/{new_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == new_id

    test_client.cookies.clear()
    test_client.headers.clear()
    test_client.post(
        f"{USER_URL}/login",
        data={"username": str(new_id), "password": "password123"},
    )

    response = test_client.get(f"{USER_URL}/{new_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == new_id


def test_update_employee_id_404_employee_not_found(
    employee_data: dict,
    test_client: TestClient,
):
    employee_id = 999

    employee_data["id"] = employee_id
    new_id = 12
    response = test_client.put(
        f"{BASE_URL}/{employee_id}/change_id/{new_id}",
        json=employee_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND


def test_delete_employee_204(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_data,
    ).json()["id"]

    response = test_client.delete(f"{BASE_URL}/{employee_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_employee_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.delete(f"{BASE_URL}/{employee_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND
