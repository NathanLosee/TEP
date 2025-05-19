from fastapi import status
from fastapi.testclient import TestClient

from src.department.constants import (
    BASE_URL,
    EXC_MSG_DEPARTMENT_NOT_FOUND,
    EXC_MSG_EMPLOYEE_IS_MEMBER,
    EXC_MSG_EMPLOYEE_NOT_MEMBER,
    EXC_MSG_EMPLOYEES_ASSIGNED,
    EXC_MSG_NAME_ALREADY_EXISTS,
)
from tests.conftest import (
    chosen_department_names,
    create_department,
    create_department_membership,
    create_employee,
    create_org_unit,
    random_string,
)


def test_create_department_201(
    department_data: dict,
    test_client: TestClient,
):
    response = test_client.post(BASE_URL, json=department_data)

    department_data["id"] = response.json()["id"]

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == department_data


def test_create_department_409_name_already_exists(
    department_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=department_data)

    response = test_client.post(BASE_URL, json=department_data)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_NAME_ALREADY_EXISTS


def test_add_employee_to_department_201(
    department_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    department = create_department(department_data, test_client)

    response = test_client.post(
        f"{BASE_URL}/{department["id"]}/employees/{employee["id"]}",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert employee in response.json()


def test_add_employee_to_department_404_department_not_found(
    test_client: TestClient,
):
    department_id = 999
    employee_id = 999

    response = test_client.post(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_add_employee_to_department_409_employee_already_member(
    department_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    department = create_department(department_data, test_client)
    create_department_membership(department["id"], employee["id"], test_client)

    response = test_client.post(
        f"{BASE_URL}/{department["id"]}/employees/{employee["id"]}",
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_IS_MEMBER


def test_get_departments_200(
    department_data: dict,
    test_client: TestClient,
):
    department = create_department(department_data, test_client)

    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert department in response.json()


def test_get_department_by_id_200(
    department_data: dict,
    test_client: TestClient,
):
    department = create_department(department_data, test_client)

    response = test_client.get(f"{BASE_URL}/{department["id"]}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == department


def test_get_department_by_id_404_department_not_found(
    test_client: TestClient,
):
    department_id = 999

    response = test_client.get(f"{BASE_URL}/{department_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_get_employees_by_department_200_empty_list(
    department_data: dict,
    test_client: TestClient,
):
    department = create_department(department_data, test_client)

    response = test_client.get(f"{BASE_URL}/{department["id"]}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_employees_by_department_200_nonempty_list(
    department_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    department = create_department(department_data, test_client)
    create_department_membership(department["id"], employee["id"], test_client)

    response = test_client.get(f"{BASE_URL}/{department["id"]}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json() == [employee]


def test_get_employees_by_department_404_department_not_found(
    test_client: TestClient,
):
    department_id = 999

    response = test_client.get(f"{BASE_URL}/{department_id}/employees")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_update_department_by_id_200(
    department_data: dict,
    test_client: TestClient,
):
    new_name = random_string(10)
    while new_name in chosen_department_names:
        new_name = random_string(10)
    chosen_department_names.append(new_name)

    department = create_department(department_data, test_client)
    department["name"] = new_name

    response = test_client.put(
        f"{BASE_URL}/{department["id"]}",
        json=department,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == department


def test_update_department_by_id_404_department_not_found(
    department_data: dict,
    test_client: TestClient,
):
    department_id = 999
    department_data["id"] = department_id

    response = test_client.put(
        f"{BASE_URL}/{department_id}",
        json=department_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_update_department_by_id_409_name_already_exists(
    department_data: dict,
    test_client: TestClient,
):
    new_name = random_string(10)
    while new_name in chosen_department_names:
        new_name = random_string(10)
    chosen_department_names.append(new_name)

    department = create_department(department_data, test_client)
    department["name"] = new_name
    department_data["name"] = new_name
    create_department(department_data, test_client)

    response = test_client.put(
        f"{BASE_URL}/{department["id"]}",
        json=department,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_NAME_ALREADY_EXISTS


def test_delete_department_by_id_204(
    department_data: dict,
    test_client: TestClient,
):
    department = create_department(department_data, test_client)

    response = test_client.delete(f"{BASE_URL}/{department["id"]}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_department_by_id_404_department_not_found(
    test_client: TestClient,
):
    department_id = 999

    response = test_client.delete(f"{BASE_URL}/{department_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_delete_department_by_id_409_employees_assigned(
    department_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    department = create_department(department_data, test_client)
    create_department_membership(department["id"], employee["id"], test_client)

    response = test_client.delete(f"{BASE_URL}/{department["id"]}")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_EMPLOYEES_ASSIGNED


def test_remove_employee_from_department_200(
    department_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    department = create_department(department_data, test_client)
    create_department_membership(department["id"], employee["id"], test_client)

    response = test_client.delete(
        f"{BASE_URL}/{department["id"]}/employees/{employee["id"]}",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_remove_employee_from_department_404_department_not_found(
    test_client: TestClient,
):
    department_id = 999
    employee_id = 999

    response = test_client.delete(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_remove_employee_from_department_404_employee_not_member(
    department_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    department = create_department(department_data, test_client)

    response = test_client.delete(
        f"{BASE_URL}/{department["id"]}/employees/{employee["id"]}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_MEMBER
