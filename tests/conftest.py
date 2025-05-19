from datetime import date
from unittest.mock import Mock, create_autospec

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import src.auth_role.repository as auth_role_repository
import src.services as services
import src.user.repository as user_repository
from src.auth_role.schemas import AuthRoleBase, PermissionBase
from src.constants import RESOURCE_SCOPES
from src.database import Base, get_db
from src.main import app, settings
from src.user.schemas import UserBase

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
        "id": 2,
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
        "user_id": 0,
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
        "employee_id": 2,
        "clock_in": date.today().isoformat(),
        "clock_out": None,
    }


@pytest.fixture
def user_data() -> dict:
    return {
        "id": 2,
        "password": "password123",
    }


@pytest.fixture
def test_client(
    test_session: Session,
):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    user_repository.create_user(
        UserBase(id=1, password=services.hash_password("password123")),
        test_session,
    )

    user_id = user_repository.create_user(
        UserBase(id=0, password=services.hash_password("password123")),
        test_session,
    ).id

    permissions = [
        PermissionBase(resource=resource) for resource in RESOURCE_SCOPES
    ]
    auth_role_id = auth_role_repository.create_auth_role(
        AuthRoleBase(name="Admin", permissions=permissions),
        test_session,
    ).id
    auth_role_repository.create_membership(auth_role_id, user_id, test_session)

    access_token = services.encode_jwt_token(
        {
            "sub": str(user_id),
            "scopes": [permission.resource for permission in permissions],
            "exp": services.get_expiration_time(True),
        },
    )
    refresh_token = services.encode_jwt_token(
        {
            "sub": str(user_id),
            "exp": services.get_expiration_time(False),
        },
    )

    test_app.headers.update({"Authorization": f"Bearer {access_token}"})
    test_app.cookies.set("refresh_token", refresh_token)
    yield test_app
