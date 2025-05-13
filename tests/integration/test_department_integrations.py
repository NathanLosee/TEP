from fastapi import status
from fastapi.testclient import TestClient
from src.department.constants import (
    BASE_URL,
    EXC_MSG_DEPARTMENT_NOT_FOUND,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_EMPLOYEE_IS_MEMBER,
    EXC_MSG_EMPLOYEE_NOT_MEMBER,
    EXC_MSG_EMPLOYEES_ASSIGNED,
)
from src.employee.constants import BASE_URL as EMPLOYEE_URL
from src.org_unit.constants import BASE_URL as ORG_UNIT_URL


def test_create_department_201(
    department_data: dict,
    test_client: TestClient,
):
    response = test_client.post(
        BASE_URL,
        json=department_data,
    )

    department_data["id"] = response.json()["id"]

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == department_data


def test_create_department_409_name_already_exists(
    department_data: dict,
    test_client: TestClient,
):
    test_client.post(
        BASE_URL,
        json=department_data,
    )

    response = test_client.post(
        BASE_URL,
        json=department_data,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_NAME_ALREADY_EXISTS


def test_create_department_membership_201(
    department_data: dict,
    org_unit_data: dict,
    employee_data: dict,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_data,
    ).json()["id"]
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]
    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]

    response = test_client.post(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_create_department_membership_404_department_not_found(
    test_client: TestClient,
):
    department_id = 999
    employee_id = 999

    response = test_client.post(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_create_department_membership_409_employee_already_member(
    department_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_data,
    ).json()["id"]
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]
    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]

    test_client.post(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    response = test_client.post(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_IS_MEMBER


def test_get_departments_200_empty_list(
    test_client: TestClient,
):
    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_departments_200_nonempty_list(
    department_data: dict,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_data,
    ).json()["id"]
    department_data["id"] = department_id

    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [department_data]


def test_get_department_200(
    department_data: dict,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_data,
    ).json()["id"]
    department_data["id"] = department_id

    response = test_client.get(f"{BASE_URL}/{department_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == department_data


def test_get_department_404_department_not_found(
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
    department_id = test_client.post(
        BASE_URL,
        json=department_data,
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{department_id}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_employees_by_department_200_nonempty_list(
    department_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_data,
    ).json()["id"]
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]
    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]

    test_client.post(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    response = test_client.get(f"{BASE_URL}/{department_id}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == employee_id


def test_get_employees_by_department_404_department_not_found(
    test_client: TestClient,
):
    department_id = 999

    response = test_client.get(f"{BASE_URL}/{department_id}/employees")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_update_department_200(
    department_data: dict,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_data,
    ).json()["id"]

    department_data["id"] = department_id
    department_data["name"] = "Updated Department Name"

    response = test_client.put(
        f"{BASE_URL}/{department_id}",
        json=department_data,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Updated Department Name"


def test_update_department_404_department_not_found(
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


def test_update_department_409_name_already_exists(
    department_data: dict,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_data,
    ).json()["id"]

    department_data["id"] = department_id
    department_data["name"] = "Updated Department Name"
    test_client.post(
        BASE_URL,
        json=department_data,
    )

    response = test_client.put(
        f"{BASE_URL}/{department_id}",
        json=department_data,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_NAME_ALREADY_EXISTS


def test_delete_department_204(
    department_data: dict,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_data,
    ).json()["id"]

    response = test_client.delete(f"{BASE_URL}/{department_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_department_404_department_not_found(
    test_client: TestClient,
):
    department_id = 999

    response = test_client.delete(f"{BASE_URL}/{department_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_delete_department_409_employees_assigned(
    department_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_data,
    ).json()["id"]
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]
    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]

    test_client.post(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    response = test_client.delete(f"{BASE_URL}/{department_id}")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_EMPLOYEES_ASSIGNED


def test_delete_department_membership_200(
    department_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_data,
    ).json()["id"]
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]
    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]

    test_client.post(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    response = test_client.delete(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_200_OK


def test_delete_department_membership_404_department_not_found(
    test_client: TestClient,
):
    department_id = 999
    employee_id = 999

    response = test_client.delete(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_delete_department_membership_404_employee_not_member(
    department_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_data,
    ).json()["id"]
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]
    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]

    response = test_client.delete(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_MEMBER
