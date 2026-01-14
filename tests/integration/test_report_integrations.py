"""Integration tests for report-related endpoints."""

from datetime import date, timedelta

from fastapi import status
from fastapi.testclient import TestClient

from src.report.constants import BASE_URL
from tests.conftest import (
    clock_employee,
    create_department,
    create_department_membership,
    create_employee,
    create_org_unit,
)


def test_create_report_200_all_employees(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    """Test generating a report for all employees."""
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    # Clock in and out
    clock_employee(employee["badge_number"], test_client)
    clock_employee(employee["badge_number"], test_client)

    # Generate report
    today = date.today()
    response = test_client.post(
        BASE_URL,
        json={
            "start_date": today.isoformat(),
            "end_date": today.isoformat(),
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["report_type"] == "employee"  # Default is employee type
    assert response.json()["start_date"] == today.isoformat()
    assert response.json()["end_date"] == today.isoformat()
    assert len(response.json()["employees"]) >= 1
    assert "generated_at" in response.json()


def test_create_report_200_single_employee(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    """Test generating a report for a specific employee."""
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    # Clock in and out
    clock_employee(employee["badge_number"], test_client)
    clock_employee(employee["badge_number"], test_client)

    # Generate report for specific employee
    today = date.today()
    response = test_client.post(
        BASE_URL,
        json={
            "start_date": today.isoformat(),
            "end_date": today.isoformat(),
            "employee_id": employee["id"],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["report_type"] == "employee"
    assert len(response.json()["employees"]) == 1
    assert response.json()["employees"][0]["employee_id"] == employee["id"]


def test_create_report_200_department(
    department_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    """Test generating a report for a department."""
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    department = create_department(department_data, test_client)
    create_department_membership(department["id"], employee["id"], test_client)

    # Clock in and out
    clock_employee(employee["badge_number"], test_client)
    clock_employee(employee["badge_number"], test_client)

    # Generate report for department
    today = date.today()
    response = test_client.post(
        BASE_URL,
        json={
            "start_date": today.isoformat(),
            "end_date": today.isoformat(),
            "department_id": department["id"],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["report_type"] == "department"
    assert len(response.json()["employees"]) == 1


def test_create_report_200_org_unit(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    """Test generating a report for an org unit."""
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    # Clock in and out
    clock_employee(employee["badge_number"], test_client)
    clock_employee(employee["badge_number"], test_client)

    # Generate report for org unit
    today = date.today()
    response = test_client.post(
        BASE_URL,
        json={
            "start_date": today.isoformat(),
            "end_date": today.isoformat(),
            "org_unit_id": org_unit["id"],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["report_type"] == "org_unit"
    assert len(response.json()["employees"]) >= 1


def test_create_report_200_empty_period(
    test_client: TestClient,
):
    """Test generating a report with no timeclock entries."""
    # Generate report for tomorrow (no entries)
    tomorrow = date.today() + timedelta(days=1)
    response = test_client.post(
        BASE_URL,
        json={
            "start_date": tomorrow.isoformat(),
            "end_date": tomorrow.isoformat(),
        },
    )

    assert response.status_code == status.HTTP_200_OK
    # May have employees but with no hours
    assert response.json()["report_type"] == "employee"


def test_create_report_200_multi_day_period(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    """Test generating a report spanning multiple days."""
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    # Clock in and out
    clock_employee(employee["badge_number"], test_client)
    clock_employee(employee["badge_number"], test_client)

    # Generate report for a week
    today = date.today()
    week_ago = today - timedelta(days=7)
    response = test_client.post(
        BASE_URL,
        json={
            "start_date": week_ago.isoformat(),
            "end_date": today.isoformat(),
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["start_date"] == week_ago.isoformat()
    assert response.json()["end_date"] == today.isoformat()


def test_export_pdf_200_summary_level(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    """Test exporting a PDF report with summary detail level."""
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    # Clock in and out
    clock_employee(employee["badge_number"], test_client)
    clock_employee(employee["badge_number"], test_client)

    # Export PDF
    today = date.today()
    response = test_client.get(
        f"{BASE_URL}/pdf",
        params={
            "start_date": today.isoformat(),
            "end_date": today.isoformat(),
            "detail_level": "summary",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/pdf"
    assert "Content-Disposition" in response.headers
    assert "timeclock_report_" in response.headers["Content-Disposition"]
    assert len(response.content) > 0  # PDF has content


def test_export_pdf_200_employee_summary_level(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    """Test exporting a PDF report with employee summary detail level."""
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    # Clock in and out
    clock_employee(employee["badge_number"], test_client)
    clock_employee(employee["badge_number"], test_client)

    # Export PDF with employee summary
    today = date.today()
    response = test_client.get(
        f"{BASE_URL}/pdf",
        params={
            "start_date": today.isoformat(),
            "end_date": today.isoformat(),
            "detail_level": "employee_summary",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0


def test_export_pdf_200_detailed_level(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    """Test exporting a PDF report with detailed level."""
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    # Clock in and out
    clock_employee(employee["badge_number"], test_client)
    clock_employee(employee["badge_number"], test_client)

    # Export PDF with detailed level
    today = date.today()
    response = test_client.get(
        f"{BASE_URL}/pdf",
        params={
            "start_date": today.isoformat(),
            "end_date": today.isoformat(),
            "detail_level": "detailed",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0


def test_export_pdf_200_single_employee(
    employee_data: dict,
    org_unit_data: dict,
    test_client: TestClient,
):
    """Test exporting a PDF report for a specific employee."""
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)

    # Clock in and out
    clock_employee(employee["badge_number"], test_client)
    clock_employee(employee["badge_number"], test_client)

    # Export PDF for specific employee
    today = date.today()
    response = test_client.get(
        f"{BASE_URL}/pdf",
        params={
            "start_date": today.isoformat(),
            "end_date": today.isoformat(),
            "employee_id": employee["id"],
            "detail_level": "detailed",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0


def test_create_report_403_no_permission(
    auth_role_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    """Test that generating reports requires permission."""
    from tests.conftest import (
        create_auth_role,
        create_auth_role_membership,
        create_user,
        login_user,
    )

    # Create user without report permission
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["badge_number"] = employee["badge_number"]
    user = create_user(user_data, test_client)

    # Create auth role without report.read permission
    auth_role_data["permissions"] = [
        {"resource": "employee.read"},
        {"resource": "event_log.read"},
    ]
    auth_role = create_auth_role(auth_role_data, test_client)
    create_auth_role_membership(auth_role["id"], user["id"], test_client)

    # Login as user without permission
    login_user(user_data, test_client)

    today = date.today()
    response = test_client.post(
        BASE_URL,
        json={
            "start_date": today.isoformat(),
            "end_date": today.isoformat(),
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
