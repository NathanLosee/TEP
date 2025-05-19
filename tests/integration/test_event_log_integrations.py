from datetime import datetime, timedelta, timezone

from fastapi import status
from fastapi.testclient import TestClient

from src.auth_role.constants import BASE_URL as AUTH_ROLE_URL
from src.employee.constants import BASE_URL as EMPLOYEE_URL
from src.event_log.constants import BASE_URL, EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND
from src.org_unit.constants import BASE_URL as ORG_UNIT_URL
from src.user.constants import BASE_URL as USER_URL


def test_create_event_log_201(
    event_log_data: dict,
    test_client: TestClient,
):
    response = test_client.post(BASE_URL, json=event_log_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["user_id"] == event_log_data["user_id"]
    assert response.json()["log"] == event_log_data["log"]


def test_get_event_logs_200_empty_list(
    test_client: TestClient,
):
    start_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
    end_timestamp = datetime.now(timezone.utc) + timedelta(days=1)

    response = test_client.get(
        BASE_URL,
        params={
            "start_timestamp": start_timestamp.isoformat(),
            "end_timestamp": end_timestamp.isoformat(),
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_event_logs_200_nonempty_list(
    event_log_data: dict,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=event_log_data)

    start_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
    end_timestamp = datetime.now(timezone.utc) + timedelta(days=1)

    response = test_client.get(
        BASE_URL,
        params={
            "start_timestamp": start_timestamp.isoformat(),
            "end_timestamp": end_timestamp.isoformat(),
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


def test_get_event_logs_200_with_user_id(
    auth_role_data: dict,
    event_log_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]

    user_data["id"] = employee_id
    test_client.post(USER_URL, json=user_data).json()["id"]

    auth_role_id = test_client.post(
        AUTH_ROLE_URL,
        json=auth_role_data,
    ).json()["id"]

    test_client.post(f"{AUTH_ROLE_URL}/{auth_role_id}/users/{employee_id}")

    test_client.post(BASE_URL, json=event_log_data)

    test_client.post(f"{USER_URL}/logout")

    test_client.cookies.clear()
    test_client.headers.clear()
    response = test_client.post(
        f"{USER_URL}/login",
        data={
            "username": str(user_data["id"]),
            "password": user_data["password"],
        },
    )
    test_client.headers["Authorization"] = (
        f"Bearer {response.json()['access_token']}"
    )

    event_log_data["user_id"] = employee_id
    event_log_data["log"] = "Another test event log"
    test_client.post(BASE_URL, json=event_log_data)

    start_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
    end_timestamp = datetime.now(timezone.utc) + timedelta(days=1)
    response = test_client.get(
        BASE_URL,
        params={
            "start_timestamp": start_timestamp.isoformat(),
            "end_timestamp": end_timestamp.isoformat(),
            "user_id": employee_id,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    # first event log is for logging in
    assert len(response.json()) == 2
    assert response.json()[1]["user_id"] == event_log_data["user_id"]
    assert response.json()[1]["log"] == event_log_data["log"]


def test_get_event_logs_200_with_log_filter(
    auth_role_data: dict,
    event_log_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]

    user_data["id"] = employee_id
    test_client.post(USER_URL, json=user_data).json()["id"]

    auth_role_id = test_client.post(
        AUTH_ROLE_URL,
        json=auth_role_data,
    ).json()["id"]

    test_client.post(f"{AUTH_ROLE_URL}/{auth_role_id}/users/{employee_id}")

    test_client.post(BASE_URL, json=event_log_data)

    test_client.post(f"{USER_URL}/logout")

    test_client.post(
        f"{USER_URL}/login",
        data={
            "username": str(user_data["id"]),
            "password": user_data["password"],
        },
    )

    event_log_data["user_id"] = employee_id
    event_log_data["log"] = "Another test event log"
    test_client.post(BASE_URL, json=event_log_data)

    start_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
    end_timestamp = datetime.now(timezone.utc) + timedelta(days=1)

    response = test_client.get(
        BASE_URL,
        params={
            "start_timestamp": start_timestamp.isoformat(),
            "end_timestamp": end_timestamp.isoformat(),
            "log_filter": "Another",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == employee_id
    assert response.json()[0]["log"] == event_log_data["log"]


def test_get_event_log_by_id_200(
    event_log_data: dict,
    test_client: TestClient,
):
    event_log_id = test_client.post(
        BASE_URL,
        json=event_log_data,
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{event_log_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user_id"] == event_log_data["user_id"]
    assert response.json()["log"] == event_log_data["log"]


def test_get_event_log_by_id_404_not_found(
    test_client: TestClient,
):
    response = test_client.get(
        f"{BASE_URL}/999999",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND


def test_delete_event_log_204(
    event_log_data: dict,
    test_client: TestClient,
):
    event_log_id = test_client.post(
        BASE_URL,
        json=event_log_data,
    ).json()["id"]

    response = test_client.delete(f"{BASE_URL}/{event_log_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_event_log_404_not_found(
    test_client: TestClient,
):
    response = test_client.delete(
        f"{BASE_URL}/999999",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND
