from datetime import datetime, timedelta, timezone
from fastapi import status
from fastapi.testclient import TestClient
from src.employee.constants import BASE_URL as EMPLOYEE_URL
from src.org_unit.constants import BASE_URL as ORG_UNIT_URL
from src.login.constants import (
    MSG_LOGOUT_SUCCESS,
    EXC_MSG_LOGIN_FAILED,
    EXC_MSG_REFRESH_TOKEN_NOT_FOUND,
    EXC_MSG_REFRESH_TOKEN_EXPIRED,
    EXC_MSG_REFRESH_TOKEN_INVALID,
)
import src.login.services as login_services


def test_login_200(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
) -> None:
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]
    employee_data["org_unit_id"] = org_unit_id
    employee_data["password"] = "password123"
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]

    login_data = {
        "username": employee_id,
        "password": employee_data["password"],
    }
    response = test_client.post("/login", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    decoded_jwt = login_services.decode_jwt_token(
        response.json()["access_token"]
    )
    assert decoded_jwt["sub"] == str(employee_id)
    decoded_jwt = login_services.decode_jwt_token(
        response.cookies["refresh_token"]
    )
    assert decoded_jwt["sub"] == str(employee_id)


def test_login_401(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
) -> None:
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]
    employee_data["org_unit_id"] = org_unit_id
    employee_data["password"] = "password123"
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]

    login_data = {"username": employee_id, "password": "wrong_password"}
    response = test_client.post("/login", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": EXC_MSG_LOGIN_FAILED}


def test_refresh_token_200(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
) -> None:
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]
    employee_data["org_unit_id"] = org_unit_id
    employee_data["password"] = "password123"
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]

    login_data = {
        "username": employee_id,
        "password": employee_data["password"],
    }
    response = test_client.post("/login", data=login_data)

    response = test_client.post("/refresh")

    assert response.status_code == status.HTTP_200_OK
    decoded_jwt = login_services.decode_jwt_token(
        response.json()["access_token"]
    )
    assert decoded_jwt["sub"] == str(employee_id)
    decoded_jwt = login_services.decode_jwt_token(
        test_client.cookies["refresh_token"]
    )
    assert decoded_jwt["sub"] == str(employee_id)


def test_refresh_token_401_refresh_token_not_found(
    test_client: TestClient,
) -> None:
    test_client.cookies.clear()
    response = test_client.post("/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == EXC_MSG_REFRESH_TOKEN_NOT_FOUND


def test_refresh_token_401_refresh_token_invalid(
    test_client: TestClient,
) -> None:
    token = login_services.encode_jwt_token(
        {"exp": datetime.now(timezone.utc) + timedelta(minutes=1)}
    )
    test_client.cookies["refresh_token"] = token

    response = test_client.post("/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == EXC_MSG_REFRESH_TOKEN_INVALID


def test_refresh_token_401_refresh_token_expired(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
) -> None:
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]
    employee_data["org_unit_id"] = org_unit_id
    employee_data["password"] = "password123"
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]
    token = login_services.encode_jwt_token(
        {
            "sub": str(employee_id),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=100),
        },
    )
    test_client.cookies["refresh_token"] = token

    response = test_client.post("/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == EXC_MSG_REFRESH_TOKEN_EXPIRED


def test_logout_200(
    test_client: TestClient,
) -> None:
    response = test_client.post("/logout")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == MSG_LOGOUT_SUCCESS
    assert "refresh_token" not in response.cookies.keys()
