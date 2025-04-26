from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.auth_role.models import AuthRole
from src.auth_role.schemas import AuthRoleExtended
from src.config import get_settings
from src.database import Base, get_db
from src.constants import HTTPMethod, ResourceType
from src.department.models import Department
from src.department.schemas import DepartmentBase, DepartmentExtended
from src.employee.models import Employee
from src.employee.schemas import EmployeeExtended
from src.holiday_group.models import HolidayGroup
from src.holiday_group.schemas import HolidayGroupExtended
from src.main import app
from src.org_unit.models import OrgUnit
from src.org_unit.schemas import OrgUnitExtended
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
        "permissions": [
            {
                "http_method": HTTPMethod.READ.value,
                "resource": ResourceType.EMPLOYEE.value,
                "restrict_to_self": True,
            },
        ],
    }


@pytest.fixture
def auth_role_extended(auth_role_data: dict) -> AuthRoleExtended:
    return AuthRoleExtended(**auth_role_data, id=1)


@pytest.fixture
def auth_role_model(auth_role_extended: AuthRoleExtended) -> AuthRole:
    return AuthRole(**auth_role_extended.model_dump())


# --- Department Fixtures ---
@pytest.fixture
def department_data() -> dict:
    return {
        "name": "Human Resources",
    }


@pytest.fixture
def department_base(department_data: dict) -> DepartmentBase:
    return DepartmentBase(**department_data)


@pytest.fixture
def department_extended(department_data: dict) -> DepartmentExtended:
    return DepartmentExtended(**department_data, id=1)


@pytest.fixture
def department_model(
    department_extended: DepartmentExtended,
) -> Department:
    return Department(**department_extended.model_dump())


# --- Employee Fixtures ---
@pytest.fixture
def employee_data() -> dict:
    return {
        "alt_id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "password": None,
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
def employee_extended(employee_data: dict) -> EmployeeExtended:
    return EmployeeExtended(**employee_data, id=1)


@pytest.fixture
def employee_model(
    employee_extended: EmployeeExtended,
) -> Employee:
    return Employee(**employee_extended.model_dump())


# --- Holiday Fixtures ---
@pytest.fixture
def holiday_group_data() -> dict:
    return {
        "name": "Public Holidays",
    }


@pytest.fixture
def holiday_data() -> dict:
    return {
        "name": "New Year's Day",
        "start_date": "2024-01-01",
        "end_date": "2024-01-01",
        "org_unit_id": 1,
    }


@pytest.fixture
def holiday_group_extended(holiday_group_data: dict) -> HolidayGroupExtended:
    return HolidayGroupExtended(**holiday_group_data, id=1, holidays=[])


@pytest.fixture
def holiday_group_model(
    holiday_group_extended: HolidayGroupExtended,
) -> HolidayGroup:
    return HolidayGroup(**holiday_group_extended.model_dump())


# --- OrgUnit Fixtures ---
@pytest.fixture
def org_unit_data() -> dict:
    return {
        "name": "Head Office",
    }


@pytest.fixture
def org_unit_extended(org_unit_data: dict) -> OrgUnitExtended:
    return OrgUnitExtended(**org_unit_data, id=1)


@pytest.fixture
def org_unit_model(
    org_unit_extended: OrgUnitExtended,
) -> OrgUnit:
    return OrgUnit(**org_unit_extended.model_dump())
