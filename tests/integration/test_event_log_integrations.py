from datetime import datetime, timedelta, timezone
from fastapi import status
from fastapi.testclient import TestClient
from src.event_log.constants import BASE_URL, EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND
from src.employee.constants import BASE_URL as EMPLOYEE_URL
from src.org_unit.constants import BASE_URL as ORG_UNIT_URL


def test_create_event_log_201(
    event_log_data: dict,
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
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]
    event_log_data["employee_id"] = employee_id

    response = test_client.post(
        BASE_URL,
        json=event_log_data,
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["employee_id"] == event_log_data["employee_id"]
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
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]
    event_log_data["employee_id"] = employee_id

    test_client.post(
        BASE_URL,
        json=event_log_data,
    )

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
    # length is 3 because of org_unit and employee needed for access token
    assert len(response.json()) == 3


def test_get_event_logs_200_with_employee_id(
    event_log_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]
    employee_data["org_unit_id"] = org_unit_id
    employee_id_1 = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]
    employee_id_2 = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]

    event_log_data["employee_id"] = employee_id_1
    test_client.post(
        BASE_URL,
        json=event_log_data,
    )

    event_log_data["employee_id"] = employee_id_2
    event_log_data["log"] = "Another test event log"
    test_client.post(
        BASE_URL,
        json=event_log_data,
    )

    start_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
    end_timestamp = datetime.now(timezone.utc) + timedelta(days=1)

    response = test_client.get(
        BASE_URL,
        params={
            "start_timestamp": start_timestamp.isoformat(),
            "end_timestamp": end_timestamp.isoformat(),
            "employee_id": employee_id_2,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["employee_id"] == event_log_data["employee_id"]
    assert response.json()[0]["log"] == event_log_data["log"]


def test_get_event_logs_200_with_log_filter(
    event_log_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_data,
    ).json()["id"]
    employee_data["org_unit_id"] = org_unit_id
    employee_id_1 = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]
    employee_id_2 = test_client.post(
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]

    event_log_data["employee_id"] = employee_id_1
    test_client.post(
        BASE_URL,
        json=event_log_data,
    )

    event_log_data["employee_id"] = employee_id_2
    event_log_data["log"] = "Another test event log"
    test_client.post(
        BASE_URL,
        json=event_log_data,
    )

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
    assert response.json()[0]["employee_id"] == employee_id_2
    assert response.json()[0]["log"] == event_log_data["log"]


def test_get_event_log_by_id_200(
    event_log_data: dict,
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
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]
    event_log_data["employee_id"] = employee_id

    event_log_id = test_client.post(
        BASE_URL,
        json=event_log_data,
    ).json()["id"]

    response = test_client.get(
        f"{BASE_URL}/{event_log_id}",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["employee_id"] == event_log_data["employee_id"]
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
        EMPLOYEE_URL,
        json=employee_data,
    ).json()["id"]
    event_log_data["employee_id"] = employee_id

    event_log_id = test_client.post(
        BASE_URL,
        json=event_log_data,
    ).json()["id"]

    response = test_client.delete(
        f"{BASE_URL}/{event_log_id}",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_event_log_404_not_found(
    test_client: TestClient,
):
    response = test_client.delete(
        f"{BASE_URL}/999999",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND
