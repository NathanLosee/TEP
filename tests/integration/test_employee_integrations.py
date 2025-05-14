from fastapi import status
from fastapi.testclient import TestClient
from src.employee.constants import BASE_URL, EXC_MSG_EMPLOYEE_NOT_FOUND
from src.auth_role.constants import BASE_URL as AUTH_ROLE_URL
from src.org_unit.constants import BASE_URL as ORG_UNIT_URL
from src.department.constants import BASE_URL as DEPARTMENT_URL
from src.holiday_group.constants import BASE_URL as HOLIDAY_GROUP_URL


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
    employee_data["id"] = employee_id

    response = test_client.get(BASE_URL)

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
    employee_data["id"] = employee_id

    response = test_client.get(f"{BASE_URL}/{employee_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == employee_data


def test_get_employee_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.get(f"{BASE_URL}/{employee_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND


def test_get_employee_auth_roles_200(
    employee_data: dict,
    org_unit_data: dict,
    auth_role_data: dict,
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

    auth_role_id = test_client.post(
        AUTH_ROLE_URL,
        json=auth_role_data,
    ).json()["id"]
    auth_role_data["id"] = auth_role_id

    test_client.post(f"{AUTH_ROLE_URL}/{auth_role_id}/employees/{employee_id}")

    response = test_client.get(f"{BASE_URL}/{employee_id}/auth_roles")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [auth_role_data]


def test_get_employee_auth_roles_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.get(f"{BASE_URL}/{employee_id}/auth_roles")

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
    org_unit_data["id"] = org_unit_id
    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_data,
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{employee_id}/org_unit")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == org_unit_data


def test_get_employee_org_unit_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.get(f"{BASE_URL}/{employee_id}/org_unit")

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
    department_data["id"] = department_id

    test_client.post(
        f"{DEPARTMENT_URL}/{department_id}/employees/{employee_id}",
    )

    response = test_client.get(f"{BASE_URL}/{employee_id}/departments")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [department_data]


def test_get_employee_departments_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.get(f"{BASE_URL}/{employee_id}/departments")

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
    holiday_group_data["id"] = holiday_group_id

    employee_data["org_unit_id"] = org_unit_id
    employee_data["holiday_group_id"] = holiday_group_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_data,
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{employee_id}/holiday_group")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == holiday_group_data


def test_get_employee_holiday_group_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.get(f"{BASE_URL}/{employee_id}/holiday_group")

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


def test_update_employee_200_with_password(
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
    employee_data["password"] = "password123"

    response = test_client.put(
        f"{BASE_URL}/{employee_id}",
        json=employee_data,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == employee_id


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
