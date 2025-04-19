from fastapi import status
from fastapi.testclient import TestClient
from src.employee.constants import BASE_URL as EMPLOYEE_URL
from src.employee.schemas import EmployeeBase
from src.login.constants import (
    MSG_LOGIN_SUCCESS,
    MSG_LOGOUT_SUCCESS,
    EXC_MSG_LOGIN_FAILED,
)
from src.login.schemas import Login
from tests.conftest import create_employee_dependencies
import src.auth as auth


def test_login_200(
    employee_base: EmployeeBase,
    test_client: TestClient,
) -> None:
    employee_base.password = "password"
    create_employee_dependencies()
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    login_data = Login(id=employee_id, password=employee_base.password)
    response = test_client.post(
        "/login",
        json=login_data.model_dump(),
    )

    decoded_jwt = auth.decode_jwt_token(response.cookies.get("auth_token"))
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == MSG_LOGIN_SUCCESS
    assert decoded_jwt["employee_id"] == employee_id


def test_login_401(
    employee_base: EmployeeBase,
    test_client: TestClient,
) -> None:
    employee_base.password = "password"
    create_employee_dependencies()
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    login_data = Login(id=employee_id, password="wrong_password")
    response = test_client.post(
        "/login",
        json=login_data.model_dump(),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": EXC_MSG_LOGIN_FAILED}


def test_logout_200(
    test_client: TestClient,
) -> None:
    response = test_client.post("/logout")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == MSG_LOGOUT_SUCCESS
