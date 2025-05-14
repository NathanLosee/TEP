from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.config import get_settings
from src.database import Base, get_db
from src.main import app
from unittest.mock import Mock, create_autospec


test_app = TestClient(app)

settings = get_settings()
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
def test_client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield test_app


# --- AuthRole Fixtures ---
@pytest.fixture
def auth_role_data() -> dict:
    return {
        "name": "Admin",
        "permissions": [{"resource": "employee.read"}],
    }


# --- Department Fixtures ---
@pytest.fixture
def department_data() -> dict:
    return {
        "name": "Human Resources",
    }


# --- Employee Fixtures ---
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


# --- Holiday Fixtures ---
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


# --- OrgUnit Fixtures ---
@pytest.fixture
def org_unit_data() -> dict:
    return {
        "name": "Head Office",
    }


# --- TimeClock Fixtures ---
@pytest.fixture
def timeclock_data() -> dict:
    return {
        "id": 1,
        "employee_id": 1,
        "clock_in": date.today().isoformat(),
        "clock_out": None,
    }
