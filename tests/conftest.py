from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.database import Base, get_db
from src.main import app, settings
from unittest.mock import Mock, create_autospec
import src.auth_role.repository as auth_role_repository
from src.auth_role.schemas import AuthRoleBase, PermissionBase
import src.employee.repository as employee_repository
from src.employee.schemas import EmployeeBase
import src.org_unit.repository as org_unit_repository
from src.org_unit.schemas import OrgUnitBase
import src.login.services as login_services


test_app = TestClient(app)
settings.ENVIRONMENT = "test"

TEST_DATABASE_URL = "sqlite:///tep_test.sqlite"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def override_get_db():
    try:
        session = TestingSessionLocal()
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def mock_session() -> tuple[Session, Mock]:
    mock_session = create_autospec(Session, instance=True)
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    return mock_session, mock_query


@pytest.fixture
def test_session():
    try:
        session = TestingSessionLocal()
        yield session
    finally:
        session.close()


@pytest.fixture
def auth_role_data() -> dict:
    return {
        "name": "Auth Role",
        "permissions": [{"resource": "employee.read"}],
    }


@pytest.fixture
def department_data() -> dict:
    return {
        "name": "Human Resources",
    }


@pytest.fixture
def employee_data() -> dict:
    return {
        "alt_id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "payroll_type": "hourly",
        "payroll_sync": date.today().isoformat(),
        "workweek_type": "standard",
        "time_type": True,
        "allow_clocking": True,
        "allow_delete": True,
        "org_unit_id": 1,
        "manager_id": None,
        "holiday_group_id": None,
    }


@pytest.fixture
def event_log_data() -> dict:
    return {
        "log": "Test event log",
        "employee_id": 1,
    }


@pytest.fixture
def holiday_group_data() -> dict:
    return {
        "name": "Public Holidays",
        "holidays": [
            {
                "name": "New Year's Day",
                "start_date": date.today().isoformat(),
                "end_date": date.today().isoformat(),
            },
            {
                "name": "Christmas Day",
                "start_date": date.today().isoformat(),
                "end_date": date.today().isoformat(),
            },
        ],
    }


@pytest.fixture
def org_unit_data() -> dict:
    return {
        "name": "Head Office",
    }


@pytest.fixture
def timeclock_data() -> dict:
    return {
        "id": 1,
        "employee_id": 1,
        "clock_in": date.today().isoformat(),
        "clock_out": None,
    }


@pytest.fixture
def test_client(
    test_session: Session,
):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    org_unit_id = org_unit_repository.create_org_unit(
        OrgUnitBase(name="Access Org Unit"),
        test_session,
    ).id

    employee_id = employee_repository.create_employee(
        EmployeeBase(
            alt_id=1,
            first_name="John",
            last_name="Doe",
            payroll_type="hourly",
            payroll_sync=date.today().isoformat(),
            workweek_type="standard",
            time_type=True,
            allow_clocking=True,
            allow_delete=True,
            org_unit_id=org_unit_id,
        ),
        test_session,
    ).id

    permissions = [
        PermissionBase(resource="auth_role.create"),
        PermissionBase(resource="auth_role.read"),
        PermissionBase(resource="auth_role.update"),
        PermissionBase(resource="auth_role.delete"),
        PermissionBase(resource="auth_role.assign"),
        PermissionBase(resource="auth_role.unassign"),
        PermissionBase(resource="department.create"),
        PermissionBase(resource="department.read"),
        PermissionBase(resource="department.update"),
        PermissionBase(resource="department.delete"),
        PermissionBase(resource="department.assign"),
        PermissionBase(resource="department.unassign"),
        PermissionBase(resource="employee.create"),
        PermissionBase(resource="employee.read"),
        PermissionBase(resource="employee.update"),
        PermissionBase(resource="employee.delete"),
        PermissionBase(resource="event_log.create"),
        PermissionBase(resource="event_log.read"),
        PermissionBase(resource="event_log.delete"),
        PermissionBase(resource="holiday_group.create"),
        PermissionBase(resource="holiday_group.read"),
        PermissionBase(resource="holiday_group.update"),
        PermissionBase(resource="holiday_group.delete"),
        PermissionBase(resource="org_unit.create"),
        PermissionBase(resource="org_unit.read"),
        PermissionBase(resource="org_unit.update"),
        PermissionBase(resource="org_unit.delete"),
        PermissionBase(resource="timeclock.update"),
        PermissionBase(resource="timeclock.delete"),
    ]
    auth_role_id = auth_role_repository.create_auth_role(
        AuthRoleBase(
            name="Admin",
            permissions=permissions,
        ),
        test_session,
    ).id
    auth_role_repository.create_membership(
        auth_role_id, employee_id, test_session
    )

    access_token = login_services.encode_jwt_token(
        {
            "sub": str(employee_id),
            "scopes": [permission.resource for permission in permissions],
            "exp": login_services.get_expiration_time(True),
        },
    )

    test_app.headers.update({"Authorization": f"Bearer {access_token}"})
    yield test_app
