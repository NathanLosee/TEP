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

    response = test_client.post(f"{BASE_URL}/{employee["badge_number"]}")

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
    clock_employee(employee["badge_number"], test_client)

    response = test_client.post(f"{BASE_URL}/{employee["badge_number"]}")

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

    response = test_client.post(f"{BASE_URL}/{employee["badge_number"]}")

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
    clock_employee(employee["badge_number"], test_client)

    response = test_client.get(f"{BASE_URL}/{employee["badge_number"]}/status")

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
    clock_employee(employee["badge_number"], test_client)
    clock_employee(employee["badge_number"], test_client)

    response = test_client.get(f"{BASE_URL}/{employee["badge_number"]}/status")

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

    response = test_client.get(f"{BASE_URL}/{employee["badge_number"]}/status")

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
    clock_employee(employee["badge_number"], test_client)

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
    entries = [entry["badge_number"] for entry in response.json()]
    assert employee["badge_number"] in entries


def test_get_timeclock_entries_200_with_employee_id(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    clock_employee(employee["badge_number"], test_client)

    start_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
    end_timestamp = datetime.now(timezone.utc) + timedelta(days=1)
    response = test_client.get(
        BASE_URL,
        params={
            "start_timestamp": start_timestamp.isoformat(),
            "end_timestamp": end_timestamp.isoformat(),
            "badge_number": employee["badge_number"],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["badge_number"] == employee["badge_number"]


def test_update_timeclock_entry_by_id_200(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    clock_employee(employee["badge_number"], test_client)

    start_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
    end_timestamp = datetime.now(timezone.utc) + timedelta(days=1)
    timeclock = test_client.get(
        BASE_URL,
        params={
            "start_timestamp": start_timestamp.isoformat(),
            "end_timestamp": end_timestamp.isoformat(),
            "badge_number": employee["badge_number"],
        },
    ).json()[0]

    new_clock_in = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    timeclock["badge_number"] = employee["badge_number"]
    timeclock["clock_in"] = new_clock_in
    del timeclock["first_name"]
    del timeclock["last_name"]

    response = test_client.put(
        f"{BASE_URL}/{timeclock["id"]}",
        json=timeclock,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == timeclock
    assert response.json()["clock_in"] == new_clock_in


def test_update_timeclock_entry_by_id_400_clock_out_before_clock_in(
    test_client: TestClient,
):
    timeclock_data = {
        "id": 999,
        "badge_number": "0",
        "clock_in": datetime.now(timezone.utc).isoformat(),
        "clock_out": (
            datetime.now(timezone.utc) - timedelta(days=1)
        ).isoformat(),
    }

    response = test_client.put(
        f"{BASE_URL}/1",
        json=timeclock_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": EXC_MSG_CLOCK_OUT_BEFORE_CLOCK_IN}


def test_update_timeclock_entry_by_id_404_not_found(
    test_client: TestClient,
):
    timeclock_data = {
        "id": 999,
        "badge_number": "0",
        "clock_in": datetime.now(timezone.utc).isoformat(),
        "clock_out": datetime.now(timezone.utc).isoformat(),
    }

    response = test_client.put(
        f"{BASE_URL}/{timeclock_data["id"]}",
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
    clock_employee(employee["badge_number"], test_client)

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


def test_clock_in_with_client_timestamp(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    client_ts = datetime(2025, 6, 15, 10, 30, 0, tzinfo=timezone.utc)
    response = test_client.post(
        f"{BASE_URL}/{employee['badge_number']}",
        json={"client_timestamp": client_ts.isoformat()},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"status": "success", "message": "Clocked in"}

    # Verify the entry uses the client timestamp
    start = client_ts - timedelta(hours=1)
    end = client_ts + timedelta(hours=1)
    entries = test_client.get(
        BASE_URL,
        params={
            "start_timestamp": start.isoformat(),
            "end_timestamp": end.isoformat(),
            "badge_number": employee["badge_number"],
        },
    ).json()

    assert len(entries) == 1
    entry_clock_in = datetime.fromisoformat(entries[0]["clock_in"])
    assert entry_clock_in.replace(tzinfo=None) == client_ts.replace(
        tzinfo=None
    )


def test_clock_out_with_client_timestamp(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    clock_in_ts = datetime(2025, 6, 15, 8, 0, 0, tzinfo=timezone.utc)
    clock_out_ts = datetime(2025, 6, 15, 17, 0, 0, tzinfo=timezone.utc)

    # Clock in with client timestamp
    test_client.post(
        f"{BASE_URL}/{employee['badge_number']}",
        json={"client_timestamp": clock_in_ts.isoformat()},
    )

    # Clock out with client timestamp
    response = test_client.post(
        f"{BASE_URL}/{employee['badge_number']}",
        json={"client_timestamp": clock_out_ts.isoformat()},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"status": "success", "message": "Clocked out"}

    # Verify both timestamps
    start = clock_in_ts - timedelta(hours=1)
    end = clock_out_ts + timedelta(hours=1)
    entries = test_client.get(
        BASE_URL,
        params={
            "start_timestamp": start.isoformat(),
            "end_timestamp": end.isoformat(),
            "badge_number": employee["badge_number"],
        },
    ).json()

    assert len(entries) == 1
    entry_in = datetime.fromisoformat(entries[0]["clock_in"])
    entry_out = datetime.fromisoformat(entries[0]["clock_out"])
    assert entry_in.replace(tzinfo=None) == clock_in_ts.replace(tzinfo=None)
    assert entry_out.replace(tzinfo=None) == clock_out_ts.replace(
        tzinfo=None
    )


def test_clock_without_timestamp_uses_server_time(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    before = datetime.now(timezone.utc)
    response = test_client.post(f"{BASE_URL}/{employee['badge_number']}")
    after = datetime.now(timezone.utc)

    assert response.status_code == status.HTTP_201_CREATED

    entries = test_client.get(
        BASE_URL,
        params={
            "start_timestamp": (before - timedelta(hours=1)).isoformat(),
            "end_timestamp": (after + timedelta(hours=1)).isoformat(),
            "badge_number": employee["badge_number"],
        },
    ).json()

    assert len(entries) == 1
    entry_clock_in = datetime.fromisoformat(entries[0]["clock_in"])
    # Server time should be between before and after
    assert before.replace(tzinfo=None) <= entry_clock_in.replace(
        tzinfo=None
    )
    assert entry_clock_in.replace(tzinfo=None) <= after.replace(tzinfo=None)


def test_sequential_offline_punches_maintain_order(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    # Simulate two offline punches: clock in at T1, clock out at T2
    t1 = datetime(2025, 7, 1, 9, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2025, 7, 1, 17, 30, 0, tzinfo=timezone.utc)

    # Clock in
    r1 = test_client.post(
        f"{BASE_URL}/{employee['badge_number']}",
        json={"client_timestamp": t1.isoformat()},
    )
    assert r1.json()["message"] == "Clocked in"

    # Clock out
    r2 = test_client.post(
        f"{BASE_URL}/{employee['badge_number']}",
        json={"client_timestamp": t2.isoformat()},
    )
    assert r2.json()["message"] == "Clocked out"

    # Verify single entry with both timestamps
    entries = test_client.get(
        BASE_URL,
        params={
            "start_timestamp": (t1 - timedelta(hours=1)).isoformat(),
            "end_timestamp": (t2 + timedelta(hours=1)).isoformat(),
            "badge_number": employee["badge_number"],
        },
    ).json()

    assert len(entries) == 1
    entry_in = datetime.fromisoformat(entries[0]["clock_in"])
    entry_out = datetime.fromisoformat(entries[0]["clock_out"])
    assert entry_in.replace(tzinfo=None) == t1.replace(tzinfo=None)
    assert entry_out.replace(tzinfo=None) == t2.replace(tzinfo=None)
