from datetime import datetime, timedelta, timezone

from fastapi import status
from fastapi.testclient import TestClient

from src.timeclock.constants import (
    BASE_URL,
    EXC_MSG_CLOCK_OUT_BEFORE_CLOCK_IN,
    EXC_MSG_EMPLOYEE_NOT_ALLOWED,
    EXC_MSG_TIMECLOCK_ENTRY_NOT_FOUND,
)
from tests.conftest import clock_employee, create_employee, create_org_unit


def test_clock_in_201(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    response = test_client.post(f"{BASE_URL}/{employee["id"]}")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"status": "success", "message": "Clocked in"}


def test_clock_out_201(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    clock_employee(employee["id"], test_client)

    response = test_client.post(f"{BASE_URL}/{employee["id"]}")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"status": "success", "message": "Clocked out"}


def test_clock_in_403_employee_not_allowed(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee_data["allow_clocking"] = False
    employee = create_employee(employee_data, test_client)

    response = test_client.post(f"{BASE_URL}/{employee["id"]}")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": EXC_MSG_EMPLOYEE_NOT_ALLOWED}


def test_check_status_200_clocked_in(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    clock_employee(employee["id"], test_client)

    response = test_client.get(f"{BASE_URL}/{employee["id"]}/status")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "success", "message": "Clocked in"}


def test_check_status_200_clocked_out(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    clock_employee(employee["id"], test_client)
    clock_employee(employee["id"], test_client)

    response = test_client.get(f"{BASE_URL}/{employee["id"]}/status")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "success", "message": "Clocked out"}


def test_check_status_403_not_allowed(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee_data["allow_clocking"] = False
    employee = create_employee(employee_data, test_client)

    response = test_client.get(f"{BASE_URL}/{employee["id"]}/status")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": EXC_MSG_EMPLOYEE_NOT_ALLOWED}


def test_get_timeclock_entries_200(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    clock_employee(employee["id"], test_client)

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
    entries = [entry["employee_id"] for entry in response.json()]
    assert employee["id"] in entries


def test_get_timeclock_entries_200_with_employee_id(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    clock_employee(employee["id"], test_client)

    start_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
    end_timestamp = datetime.now(timezone.utc) + timedelta(days=1)
    response = test_client.get(
        BASE_URL,
        params={
            "start_timestamp": start_timestamp.isoformat(),
            "end_timestamp": end_timestamp.isoformat(),
            "employee_id": employee["id"],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["employee_id"] == employee["id"]


def test_update_timeclock_entry_by_id_200(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    clock_employee(employee["id"], test_client)

    start_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
    end_timestamp = datetime.now(timezone.utc) + timedelta(days=1)
    timeclock = test_client.get(
        BASE_URL,
        params={
            "start_timestamp": start_timestamp.isoformat(),
            "end_timestamp": end_timestamp.isoformat(),
            "employee_id": employee["id"],
        },
    ).json()[0]

    new_clock_in = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    timeclock["employee_id"] = employee["id"]
    timeclock["clock_in"] = new_clock_in

    response = test_client.put(
        f"{BASE_URL}/{timeclock["id"]}",
        json=timeclock,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == timeclock
    assert response.json()["clock_in"] == new_clock_in


def test_update_timeclock_entry_by_id_400_clock_out_before_clock_in(
    timeclock_data: dict,
    test_client: TestClient,
):
    timeclock_data["employee_id"] = 1
    timeclock_data["clock_in"] = datetime.now(timezone.utc).isoformat()
    timeclock_data["clock_out"] = (
        datetime.now(timezone.utc) - timedelta(days=1)
    ).isoformat()

    response = test_client.put(
        f"{BASE_URL}/1",
        json=timeclock_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": EXC_MSG_CLOCK_OUT_BEFORE_CLOCK_IN}


def test_update_timeclock_entry_by_id_404_not_found(
    timeclock_data: dict,
    test_client: TestClient,
):
    timeclock_id = 999
    timeclock_data["id"] = timeclock_id
    timeclock_data["employee_id"] = 1

    response = test_client.put(
        f"{BASE_URL}/{timeclock_id}",
        json=timeclock_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_TIMECLOCK_ENTRY_NOT_FOUND}


def test_delete_timeclock_entry_by_id_204(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    clock_employee(employee["id"], test_client)

    start_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
    end_timestamp = datetime.now(timezone.utc) + timedelta(days=1)
    timeclock_id = test_client.get(
        BASE_URL,
        params={
            "start_timestamp": start_timestamp.isoformat(),
            "end_timestamp": end_timestamp.isoformat(),
        },
    ).json()[0]["id"]

    response = test_client.delete(
        f"{BASE_URL}/{timeclock_id}",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_timeclock_entry_by_id_404_not_found(
    test_client: TestClient,
):
    timeclock_id = 999

    response = test_client.delete(f"{BASE_URL}/{timeclock_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_TIMECLOCK_ENTRY_NOT_FOUND}
