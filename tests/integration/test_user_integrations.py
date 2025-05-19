from datetime import datetime, timedelta, timezone

from fastapi import status
from fastapi.testclient import TestClient

import src.services as services
from src.auth_role.constants import BASE_URL as AUTH_ROLE_URL
from src.constants import EXC_MSG_IDS_DO_NOT_MATCH
from src.employee.constants import BASE_URL as EMPLOYEE_URL
from src.user.constants import (
    BASE_URL,
    EXC_MSG_ACCESS_TOKEN_INVALID,
    EXC_MSG_LOGIN_FAILED,
    EXC_MSG_MISSING_PERMISSION,
    EXC_MSG_REFRESH_TOKEN_INVALID,
    EXC_MSG_REFRESH_TOKEN_NOT_FOUND,
    EXC_MSG_TOKEN_EXPIRED,
    EXC_MSG_USER_NOT_FOUND,
    EXC_MSG_USER_WITH_ID_EXISTS,
    EXC_MSG_WRONG_PASSWORD,
    MSG_LOGOUT_SUCCESS,
)


def test_create_user_201(
    user_data: dict,
    test_client: TestClient,
):
    response = test_client.post(BASE_URL, json=user_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"id": user_data["id"]}


def test_create_user_409_user_already_exists(
    user_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=user_data)

    response = test_client.post(BASE_URL, json=user_data)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": EXC_MSG_USER_WITH_ID_EXISTS}


def test_get_users_200(
    user_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=user_data)

    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    # account for the root user and timeclock user
    assert len(response.json()) == 3
    assert {"id": user_data["id"]} in response.json()


def test_get_user_by_id_200(
    user_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=user_data)

    response = test_client.get(f"{BASE_URL}/{user_data['id']}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": user_data["id"]}


def test_get_user_by_id_404_id_not_found(
    test_client: TestClient,
):
    user_id = 999

    response = test_client.get(f"{BASE_URL}/{user_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_USER_NOT_FOUND}


def test_get_user_auth_roles_200_empty_list(
    user_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=user_data)

    response = test_client.get(f"{BASE_URL}/{user_data['id']}/auth_roles")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_user_auth_roles_200_nonempty_list(
    auth_role_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=user_data)

    auth_role_id = test_client.post(
        AUTH_ROLE_URL,
        json=auth_role_data,
    ).json()["id"]

    test_client.post(f"{AUTH_ROLE_URL}/{auth_role_id}/users/{user_data['id']}")

    response = test_client.get(f"{BASE_URL}/{user_data['id']}/auth_roles")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == auth_role_id


def test_get_user_auth_roles_404_user_not_found(
    test_client: TestClient,
):
    user_id = 999

    response = test_client.get(f"{BASE_URL}/{user_id}/auth_roles")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_USER_NOT_FOUND}


def test_update_user_200(
    user_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=user_data)

    user_data["password"] = "new_password"
    response = test_client.put(f"{BASE_URL}/{user_data['id']}", json=user_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": user_data["id"]}

    test_client.cookies.clear()
    test_client.headers.clear()
    login_data = {
        "username": str(user_data["id"]),
        "password": user_data["password"],
    }
    response = test_client.post(f"{BASE_URL}/login", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    decoded_jwt = services.decode_jwt_token(response.json()["access_token"])
    assert decoded_jwt["sub"] == str(user_data["id"])
    decoded_jwt = services.decode_jwt_token(
        test_client.cookies["refresh_token"]
    )
    assert decoded_jwt["sub"] == str(user_data["id"])


def test_update_user_400_ids_do_not_match(
    user_data: dict,
    test_client: TestClient,
):
    user_data["id"] = 999

    response = test_client.put(f"{BASE_URL}/0", json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": EXC_MSG_IDS_DO_NOT_MATCH}


def test_update_user_404_user_not_found(
    user_data: dict,
    test_client: TestClient,
):
    user_data["id"] = 999

    response = test_client.put(f"{BASE_URL}/{user_data['id']}", json=user_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_USER_NOT_FOUND}


def test_update_user_password_200(
    user_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=user_data)

    test_client.cookies.clear()
    test_client.headers.clear()
    user_data["new_password"] = "new_password"
    response = test_client.put(
        f"{BASE_URL}/{user_data['id']}/password", json=user_data
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": user_data["id"]}

    login_data = {
        "username": str(user_data["id"]),
        "password": user_data["new_password"],
    }
    response = test_client.post(f"{BASE_URL}/login", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    decoded_jwt = services.decode_jwt_token(response.json()["access_token"])
    assert decoded_jwt["sub"] == str(user_data["id"])
    decoded_jwt = services.decode_jwt_token(
        test_client.cookies["refresh_token"]
    )
    assert decoded_jwt["sub"] == str(user_data["id"])


def test_update_user_password_400_ids_do_not_match(
    user_data: dict,
    test_client: TestClient,
):
    user_data["id"] = 999
    user_data["new_password"] = "new_password"

    response = test_client.put(f"{BASE_URL}/0/password", json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": EXC_MSG_IDS_DO_NOT_MATCH}


def test_update_user_password_404_user_not_found(
    user_data: dict,
    test_client: TestClient,
):
    user_data["id"] = 999
    user_data["new_password"] = "new_password"

    response = test_client.put(
        f"{BASE_URL}/{user_data['id']}/password", json=user_data
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_USER_NOT_FOUND}


def test_update_user_password_400_wrong_password(
    user_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=user_data)

    user_data["new_password"] = "new_password"
    user_data["password"] = "wrong_password"

    response = test_client.put(
        f"{BASE_URL}/{user_data['id']}/password", json=user_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": EXC_MSG_WRONG_PASSWORD}


def test_delete_user_204(
    user_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=user_data)

    response = test_client.delete(f"{BASE_URL}/{user_data['id']}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_user_404_user_not_found(
    test_client: TestClient,
):
    user_id = 999

    response = test_client.delete(f"{BASE_URL}/{user_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_USER_NOT_FOUND}


def test_login_200(
    user_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=user_data)

    test_client.headers.clear()
    test_client.cookies.clear()
    login_data = {
        "username": str(user_data["id"]),
        "password": user_data["password"],
    }
    response = test_client.post(f"{BASE_URL}/login", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    decoded_jwt = services.decode_jwt_token(response.json()["access_token"])
    assert decoded_jwt["sub"] == str(user_data["id"])
    decoded_jwt = services.decode_jwt_token(
        test_client.cookies["refresh_token"]
    )
    assert decoded_jwt["sub"] == str(user_data["id"])


def test_login_401(
    user_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=user_data)

    login_data = {
        "username": str(user_data["id"]),
        "password": "wrong_password",
    }
    response = test_client.post(f"{BASE_URL}/login", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": EXC_MSG_LOGIN_FAILED}


def test_refresh_token_200(
    user_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=user_data)

    test_client.headers.clear()
    test_client.cookies.clear()
    login_data = {
        "username": str(user_data["id"]),
        "password": user_data["password"],
    }
    response = test_client.post(f"{BASE_URL}/login", data=login_data)

    test_client.headers.update(
        {"Authorization": f"Bearer {response.json()['access_token']}"}
    )
    response = test_client.post(f"{BASE_URL}/refresh")

    assert response.status_code == status.HTTP_200_OK
    decoded_jwt = services.decode_jwt_token(
        test_client.headers["Authorization"].split(" ")[1]
    )
    assert decoded_jwt["sub"] == str(user_data["id"])
    decoded_jwt = services.decode_jwt_token(
        test_client.cookies["refresh_token"]
    )
    assert decoded_jwt["sub"] == str(user_data["id"])


def test_refresh_token_401_refresh_token_not_found(
    test_client: TestClient,
):
    test_client.cookies.clear()
    response = test_client.post(f"{BASE_URL}/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == EXC_MSG_REFRESH_TOKEN_NOT_FOUND


def test_refresh_token_401_refresh_token_invalid(
    test_client: TestClient,
):
    token = services.encode_jwt_token(
        {"exp": datetime.now(timezone.utc) + timedelta(minutes=1)}
    )
    test_client.cookies["refresh_token"] = token

    response = test_client.post(f"{BASE_URL}/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == EXC_MSG_REFRESH_TOKEN_INVALID


def test_refresh_token_401_refresh_token_expired(
    user_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=user_data)

    token = services.encode_jwt_token(
        {
            "sub": str(user_data["id"]),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=100),
        },
    )
    test_client.cookies["refresh_token"] = token

    response = test_client.post(f"{BASE_URL}/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == EXC_MSG_TOKEN_EXPIRED


def test_logout_200(
    employee_data: dict,
    test_client: TestClient,
):
    response = test_client.post(f"{BASE_URL}/logout")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == MSG_LOGOUT_SUCCESS

    response = test_client.post(f"{BASE_URL}/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == EXC_MSG_REFRESH_TOKEN_INVALID

    response = test_client.post(f"{EMPLOYEE_URL}", json=employee_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == EXC_MSG_ACCESS_TOKEN_INVALID


def test_create_employee_403_missing_permission(
    auth_role_data: dict,
    employee_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=user_data)

    auth_role_id = test_client.post(
        AUTH_ROLE_URL,
        json=auth_role_data,
    ).json()["id"]
    test_client.post(f"{AUTH_ROLE_URL}/{auth_role_id}/users/{user_data['id']}")

    test_client.headers.clear()
    test_client.cookies.clear()
    login_data = {
        "username": str(user_data["id"]),
        "password": user_data["password"],
    }
    response = test_client.post(f"{BASE_URL}/login", data=login_data)

    test_client.headers.update(
        {"Authorization": f"Bearer {response.json()['access_token']}"}
    )
    response = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == EXC_MSG_MISSING_PERMISSION
