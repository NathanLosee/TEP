from datetime import datetime, timedelta, timezone

from fastapi import status
from fastapi.testclient import TestClient

import src.services as services
from src.constants import EXC_MSG_IDS_DO_NOT_MATCH
from src.user.constants import (
    BASE_URL,
    EXC_MSG_ACCESS_TOKEN_INVALID,
    EXC_MSG_ACCESS_TOKEN_NOT_FOUND,
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
from tests.conftest import (
    create_auth_role,
    create_auth_role_membership,
    create_employee,
    create_org_unit,
    create_user,
    login_user,
)


def test_create_user_201(
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["badge_number"] = employee["badge_number"]

    response = test_client.post(BASE_URL, json=user_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": response.json()["id"],
        "badge_number": user_data["badge_number"],
    }


def test_create_user_409_user_already_exists(
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["badge_number"] = employee["badge_number"]
    create_user(user_data, test_client)

    response = test_client.post(BASE_URL, json=user_data)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": EXC_MSG_USER_WITH_ID_EXISTS}


def test_get_users_200(
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["badge_number"] = employee["badge_number"]
    user = create_user(user_data, test_client)

    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert user in response.json()


def test_get_user_by_id_200(
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["badge_number"] = employee["badge_number"]
    user = create_user(user_data, test_client)

    response = test_client.get(f"{BASE_URL}/{user["id"]}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == user


def test_get_user_by_id_404_user_not_found(
    test_client: TestClient,
):
    user_id = 999

    response = test_client.get(f"{BASE_URL}/{user_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_USER_NOT_FOUND}


def test_get_user_auth_roles_200_empty_list(
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["badge_number"] = employee["badge_number"]
    user = create_user(user_data, test_client)

    response = test_client.get(f"{BASE_URL}/{user["id"]}/auth_roles")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_user_auth_roles_200_nonempty_list(
    auth_role_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["badge_number"] = employee["badge_number"]
    user = create_user(user_data, test_client)
    auth_role = create_auth_role(auth_role_data, test_client)
    create_auth_role_membership(auth_role["id"], user["id"], test_client)

    response = test_client.get(f"{BASE_URL}/{user["id"]}/auth_roles")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [auth_role]


def test_get_user_auth_roles_404_user_not_found(
    test_client: TestClient,
):
    user_id = 999

    response = test_client.get(f"{BASE_URL}/{user_id}/auth_roles")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_USER_NOT_FOUND}


def test_update_user_password_200(
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["badge_number"] = employee["badge_number"]
    user = create_user(user_data, test_client)
    user_data["new_password"] = "new_password"

    test_client.cookies.clear()
    test_client.headers.clear()
    response = test_client.put(
        f"{BASE_URL}/{user["badge_number"]}",
        json=user_data,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": user["id"],
        "badge_number": user["badge_number"],
    }

    user_data["password"] = "new_password"
    login_user(user_data, test_client)

    assert response.status_code == status.HTTP_200_OK

    decoded_jwt = services.decode_jwt_token(
        test_client.headers["Authorization"].split(" ")[1]
    )
    assert decoded_jwt["sub"] == user["badge_number"]

    decoded_jwt = services.decode_jwt_token(
        test_client.cookies["refresh_token"]
    )
    assert decoded_jwt["sub"] == user["badge_number"]


def test_update_user_password_400_ids_do_not_match(
    user_data: dict,
    test_client: TestClient,
):
    user_data["badge_number"] = "0"
    user_data["new_password"] = "new_password"

    response = test_client.put(f"{BASE_URL}/1", json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": EXC_MSG_IDS_DO_NOT_MATCH}


def test_update_user_password_404_user_not_found(
    user_data: dict,
    test_client: TestClient,
):
    user_data["badge_number"] = "999"
    user_data["new_password"] = "new_password"

    response = test_client.put(
        f"{BASE_URL}/{user_data["badge_number"]}", json=user_data
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_USER_NOT_FOUND}


def test_update_user_password_403_wrong_password(
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["badge_number"] = employee["badge_number"]
    test_client.post(BASE_URL, json=user_data)
    user_data["password"] = "wrong_password"
    user_data["new_password"] = "new_password"

    response = test_client.put(
        f"{BASE_URL}/{user_data["badge_number"]}", json=user_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": EXC_MSG_WRONG_PASSWORD}


def test_delete_user_by_id_204(
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["badge_number"] = employee["badge_number"]
    user = create_user(user_data, test_client)

    response = test_client.delete(f"{BASE_URL}/{user["id"]}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_user_by_id_404_user_not_found(
    test_client: TestClient,
):
    user_id = 999

    response = test_client.delete(f"{BASE_URL}/{user_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_USER_NOT_FOUND}


def test_login_200(
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["badge_number"] = employee["badge_number"]
    user = create_user(user_data, test_client)

    test_client.headers.clear()
    test_client.cookies.clear()
    login_data = {
        "username": user["badge_number"],
        "password": user_data["password"],
    }
    response = test_client.post(f"{BASE_URL}/login", data=login_data)
    test_client.headers.update(
        {"Authorization": f"Bearer {response.json()['access_token']}"}
    )

    assert response.status_code == status.HTTP_200_OK

    decoded_jwt = services.decode_jwt_token(
        test_client.headers["Authorization"].split(" ")[1]
    )
    assert decoded_jwt["sub"] == user["badge_number"]

    decoded_jwt = services.decode_jwt_token(
        test_client.cookies["refresh_token"]
    )
    assert decoded_jwt["sub"] == user["badge_number"]


def test_login_401(
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["badge_number"] = employee["badge_number"]
    user = create_user(user_data, test_client)

    login_data = {
        "username": str(user["id"]),
        "password": "wrong_password",
    }
    response = test_client.post(f"{BASE_URL}/login", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": EXC_MSG_LOGIN_FAILED}


def test_refresh_token_200(
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["badge_number"] = employee["badge_number"]
    user = create_user(user_data, test_client)
    login_user(user_data, test_client)

    response = test_client.post(f"{BASE_URL}/refresh")

    assert response.status_code == status.HTTP_200_OK

    decoded_jwt = services.decode_jwt_token(
        test_client.headers["Authorization"].split(" ")[1]
    )
    assert decoded_jwt["sub"] == user["badge_number"]

    decoded_jwt = services.decode_jwt_token(
        test_client.cookies["refresh_token"]
    )
    assert decoded_jwt["sub"] == user["badge_number"]


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
        "INVALID_USER",
        datetime.now(timezone.utc) + timedelta(minutes=1),
    )
    test_client.cookies["refresh_token"] = token

    response = test_client.post(f"{BASE_URL}/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == EXC_MSG_REFRESH_TOKEN_INVALID


def test_refresh_token_401_refresh_token_expired(
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["badge_number"] = employee["badge_number"]
    user = create_user(user_data, test_client)

    token = services.encode_jwt_token(
        user["badge_number"],
        datetime.now(timezone.utc) - timedelta(minutes=100),
    )
    test_client.cookies["refresh_token"] = token

    response = test_client.post(f"{BASE_URL}/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # Expired token is detected as invalid
    assert response.json()["detail"] == EXC_MSG_REFRESH_TOKEN_INVALID


def test_logout_200(
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["badge_number"] = employee["badge_number"]
    create_user(user_data, test_client)
    login_user(user_data, test_client)

    response = test_client.post(f"{BASE_URL}/logout")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == MSG_LOGOUT_SUCCESS

    response = test_client.post(f"{BASE_URL}/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == EXC_MSG_REFRESH_TOKEN_INVALID

    # Clear headers to test unauthorized access
    test_client.headers.clear()
    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # FastAPI OAuth2 returns generic message
    assert response.json()["detail"] == "Not authenticated"


def test_logout_401_access_token_not_found(
    test_client: TestClient,
):
    test_client.headers.clear()
    test_client.cookies.clear()

    response = test_client.post(f"{BASE_URL}/logout")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == EXC_MSG_ACCESS_TOKEN_NOT_FOUND


def test_logout_401_refresh_token_not_found(
    test_client: TestClient,
):
    test_client.cookies.clear()

    response = test_client.post(f"{BASE_URL}/logout")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == EXC_MSG_REFRESH_TOKEN_NOT_FOUND


def test_create_employee_403_missing_permission(
    auth_role_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["badge_number"] = employee["badge_number"]
    user = create_user(user_data, test_client)
    auth_role = create_auth_role(auth_role_data, test_client)
    create_auth_role_membership(auth_role["id"], user["id"], test_client)
    login_user(user_data, test_client)

    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == EXC_MSG_MISSING_PERMISSION
