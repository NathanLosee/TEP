from datetime import datetime, timedelta, timezone

from fastapi import status
from fastapi.testclient import TestClient

from src.event_log.constants import BASE_URL, EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND


def test_create_event_log_201(
    event_log_data: dict,
    test_client: TestClient,
):
    event_log_data["badge_number"] = "0"

    response = test_client.post(BASE_URL, json=event_log_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["badge_number"] == event_log_data["badge_number"]
    assert response.json()["log"] == event_log_data["log"]


def test_get_event_logs_200(
    event_log_data: dict,
    test_client: TestClient,
):
    event_log_data["badge_number"] = "0"
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
    assert event_log_data in [
        {"badge_number": log["badge_number"], "log": log["log"]}
        for log in response.json()
    ]


def test_get_event_logs_200_with_user_id(
    event_log_data: dict,
    test_client: TestClient,
):
    event_log_data["badge_number"] = "0"
    event_log_data["log"] = "Another test event log"
    test_client.post(BASE_URL, json=event_log_data)

    start_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
    end_timestamp = datetime.now(timezone.utc) + timedelta(days=1)
    response = test_client.get(
        BASE_URL,
        params={
            "start_timestamp": start_timestamp.isoformat(),
            "end_timestamp": end_timestamp.isoformat(),
            "badge_number": "0",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert event_log_data in [
        {"badge_number": log["badge_number"], "log": log["log"]}
        for log in response.json()
    ]


def test_get_event_logs_200_with_log_filter(
    event_log_data: dict,
    test_client: TestClient,
):
    event_log_data["badge_number"] = "0"
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
    assert event_log_data in [
        {"badge_number": log["badge_number"], "log": log["log"]}
        for log in response.json()
    ]


def test_get_event_log_by_id_200(
    event_log_data: dict,
    test_client: TestClient,
):
    event_log_data["badge_number"] = "0"
    event_log_id = test_client.post(
        BASE_URL,
        json=event_log_data,
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{event_log_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["badge_number"] == event_log_data["badge_number"]
    assert response.json()["log"] == event_log_data["log"]


def test_get_event_log_by_id_404_not_found(
    test_client: TestClient,
):
    response = test_client.get(
        f"{BASE_URL}/999999",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND


def test_delete_event_log_by_id_204(
    event_log_data: dict,
    test_client: TestClient,
):
    event_log_data["badge_number"] = "0"
    event_log_id = test_client.post(
        BASE_URL,
        json=event_log_data,
    ).json()["id"]

    response = test_client.delete(f"{BASE_URL}/{event_log_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_event_log_by_id_404_not_found(
    test_client: TestClient,
):
    response = test_client.delete(
        f"{BASE_URL}/999999",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND
