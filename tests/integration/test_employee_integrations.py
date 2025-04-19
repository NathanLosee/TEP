from fastapi import status
from fastapi.testclient import TestClient
from src.employee.constants import BASE_URL, EXC_MSG_EMPLOYEE_NOT_FOUND
from src.employee.schemas import (
    EmployeeBase,
    EmployeeExtended,
)
from tests.conftest import create_employee_dependencies


def test_create_employee_201(
    employee_base: EmployeeBase,
    employee_extended: EmployeeExtended,
    test_client: TestClient,
):
    create_employee_dependencies()
    response = test_client.post(
        BASE_URL,
        json=employee_base.model_dump(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == employee_extended.model_dump()


def test_get_employees_200_empty_list(
    test_client: TestClient,
):
    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_employees_200_nonempty_list(
    employee_base: EmployeeBase,
    employee_extended: EmployeeExtended,
    test_client: TestClient,
):
    create_employee_dependencies()
    test_client.post(
        BASE_URL,
        json=employee_base.model_dump(),
    )

    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [employee_extended.model_dump()]


def test_get_employee_200(
    employee_base: EmployeeBase,
    employee_extended: EmployeeExtended,
    test_client: TestClient,
):
    create_employee_dependencies()
    employee_id = test_client.post(
        BASE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{employee_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == employee_extended.model_dump()


def test_get_employee_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.get(f"{BASE_URL}/{employee_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND


def test_update_employee_200(
    employee_base: EmployeeBase,
    test_client: TestClient,
):
    create_employee_dependencies()
    employee_id = test_client.post(
        BASE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    employee_base.first_name = "Updated Employee Name"

    response = test_client.put(
        f"{BASE_URL}/{employee_id}",
        json=employee_base.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["first_name"] == "Updated Employee Name"


def test_update_employee_404_employee_not_found(
    employee_base: EmployeeBase,
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.put(
        f"{BASE_URL}/{employee_id}",
        json=employee_base.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND


def test_delete_employee_204(
    employee_base: EmployeeBase,
    test_client: TestClient,
):
    create_employee_dependencies()
    employee_id = test_client.post(
        BASE_URL,
        json=employee_base.model_dump(),
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
