import random

from fastapi import status
from fastapi.testclient import TestClient

from src.employee.constants import BASE_URL, EXC_MSG_EMPLOYEE_NOT_FOUND
from tests.conftest import (
    chosen_employee_ids,
    clock_employee,
    create_auth_role,
    create_auth_role_membership,
    create_department,
    create_department_membership,
    create_employee,
    create_holiday_group,
    create_org_unit,
    create_user,
    login_user,
)


def test_create_employee_201(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]

    response = test_client.post(
        BASE_URL,
        json=employee_data,
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == employee_data


def test_get_employees_200(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert employee in response.json()


def test_get_employee_by_id_200(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    response = test_client.get(f"{BASE_URL}/{employee["id"]}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == employee


def test_get_employee_by_id_404_employee_not_found(
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
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    department = create_department(department_data, test_client)
    create_department_membership(department["id"], employee["id"], test_client)

    response = test_client.get(f"{BASE_URL}/{employee["id"]}/departments")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [department["name"]]


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
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    response = test_client.get(f"{BASE_URL}/{employee["id"]}/org_unit")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == org_unit["name"]


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
    holiday_group = create_holiday_group(holiday_group_data, test_client)
    employee_data["holiday_group_id"] = holiday_group["id"]
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    response = test_client.get(f"{BASE_URL}/{employee["id"]}/holiday_group")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == holiday_group["name"]


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
    new_id = random.randint(2, 1000000)
    while new_id in chosen_employee_ids:
        new_id = random.randint(2, 1000000)
    chosen_employee_ids.append(new_id)

    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee_data["first_name"] = "Test"
    employee_data["last_name"] = "Manager"
    manager = create_employee(employee_data, test_client)
    employee_data["id"] = new_id
    employee_data["first_name"] = "Test"
    employee_data["last_name"] = "Employee"
    employee_data["manager_id"] = manager["id"]
    employee = create_employee(employee_data, test_client)

    response = test_client.get(f"{BASE_URL}/{employee["id"]}/manager")

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


def test_update_employee_by_id_200(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    employee["first_name"] = "Updated Employee Name"

    response = test_client.put(
        f"{BASE_URL}/{employee["id"]}",
        json=employee,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == employee
    assert response.json()["first_name"] == "Updated Employee Name"


def test_update_employee_by_id_404_employee_not_found(
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
    new_id = random.randint(2, 1000000)
    while new_id in chosen_employee_ids:
        new_id = random.randint(2, 1000000)
    chosen_employee_ids.append(new_id)

    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    department = create_department(department_data, test_client)
    create_department_membership(department["id"], employee["id"], test_client)
    clock_employee(employee["id"], test_client)

    response = test_client.put(
        f"{BASE_URL}/{employee["id"]}/change_id/{new_id}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == new_id


def test_update_employee_id_200_with_user(
    auth_role_data: dict,
    org_unit_data: dict,
    employee_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    new_id = random.randint(2, 1000000)
    while new_id in chosen_employee_ids:
        new_id = random.randint(2, 1000000)
    chosen_employee_ids.append(new_id)

    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["id"] = employee["id"]
    user = create_user(user_data, test_client)
    auth_role = create_auth_role(auth_role_data, test_client)
    create_auth_role_membership(auth_role["id"], user["id"], test_client)

    response = test_client.put(
        f"{BASE_URL}/{employee["id"]}/change_id/{new_id}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == new_id

    user_data["id"] = new_id
    login_user(user_data, test_client)
    response = test_client.get(f"{BASE_URL}/{new_id}")

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


def test_delete_employee_by_id_204(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    response = test_client.delete(f"{BASE_URL}/{employee["id"]}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_employee_by_id_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.delete(f"{BASE_URL}/{employee_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND
