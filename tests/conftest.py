import random
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src import services
from src.auth_role.constants import BASE_URL as AUTH_ROLE_URL
from src.auth_role.models import (
    AuthRole,
    AuthRoleMembership,
    AuthRolePermission,
)
from src.constants import RESOURCE_SCOPES
from src.database import Base, get_db
from src.department.constants import BASE_URL as DEPARTMENT_URL
from src.employee.constants import BASE_URL as EMPLOYEE_URL
from src.employee.models import Employee
from src.event_log.constants import BASE_URL as EVENT_LOG_URL
from src.holiday_group.constants import BASE_URL as HOLIDAY_GROUP_URL
from src.main import app, settings
from src.org_unit.constants import BASE_URL as ORG_UNIT_URL
from src.org_unit.models import OrgUnit
from src.timeclock.constants import BASE_URL as TIMECLOCK_URL
from src.user.constants import BASE_URL as USER_URL
from src.user.models import User

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


letters = "abcdefghijklmnopqrstuvwxyz"


def random_string(length: int) -> str:
    """Generate a random string of lowercase letters.

    Args:
        length (int): The length of the random string.

    Returns:
        str: A random string of lowercase letters.
    """
    return "".join(random.choice(letters) for _ in range(length))


chosen_auth_role_names = []
chosen_department_names = []
chosen_badge_numbers = []
chosen_holiday_group_names = []
chosen_org_unit_names = []


def generate_unique_string(existing_names: list, length: int) -> str:
    """Generate a unique string that is not in the existing names list.

    Args:
        existing_names (list): List of existing names to avoid.
        length (int): Length of the random string.

    Returns:
        str: A unique random string.
    """
    name = random_string(length)
    while name in existing_names:
        name = random_string(length)
    return name


@pytest.fixture
def auth_role_data() -> dict:
    return {
        "name": generate_unique_string(chosen_auth_role_names, 10),
        "permissions": [
            {"resource": "employee.read"},
            {"resource": "event_log.create"},
            {"resource": "event_log.read"},
        ],
    }


def create_auth_role(auth_role_data: dict, test_client: TestClient) -> dict:
    return test_client.post(AUTH_ROLE_URL, json=auth_role_data).json()


def create_auth_role_membership(
    auth_role_id: int, user_id: int, test_client: TestClient
) -> dict:
    test_client.post(f"{AUTH_ROLE_URL}/{auth_role_id}/users/{user_id}")


@pytest.fixture
def department_data() -> dict:
    return {"name": generate_unique_string(chosen_department_names, 10)}


def create_department(department_data: dict, test_client: TestClient) -> dict:
    return test_client.post(DEPARTMENT_URL, json=department_data).json()


def create_department_membership(
    department_id: int, user_id: int, test_client: TestClient
) -> dict:
    test_client.post(f"{DEPARTMENT_URL}/{department_id}/employees/{user_id}")


@pytest.fixture
def employee_data() -> dict:
    return {
        "badge_number": generate_unique_string(chosen_badge_numbers, 10),
        "first_name": random_string(10),
        "last_name": random_string(10),
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


def create_employee(employee_data: dict, test_client: TestClient) -> dict:
    return test_client.post(EMPLOYEE_URL, json=employee_data).json()


@pytest.fixture
def event_log_data() -> dict:
    return {
        "log": random_string(10),
        "badge_number": None,
    }


def create_event_log(event_log_data: dict, test_client: TestClient) -> dict:
    return test_client.post(EVENT_LOG_URL, json=event_log_data).json()


@pytest.fixture
def holiday_group_data() -> dict:
    return {
        "name": generate_unique_string(chosen_holiday_group_names, 10),
        "holidays": [
            {
                "name": random_string(10),
                "start_date": date.today().isoformat(),
                "end_date": date.today().isoformat(),
            },
        ],
    }


def create_holiday_group(
    holiday_group_data: dict, test_client: TestClient
) -> dict:
    return test_client.post(HOLIDAY_GROUP_URL, json=holiday_group_data).json()


@pytest.fixture
def org_unit_data() -> dict:
    return {"name": generate_unique_string(chosen_org_unit_names, 10)}


def create_org_unit(org_unit_data: dict, test_client: TestClient) -> dict:
    return test_client.post(ORG_UNIT_URL, json=org_unit_data).json()


def clock_employee(badge_number: str, test_client: TestClient) -> dict:
    return test_client.post(f"{TIMECLOCK_URL}/{badge_number}").json()


@pytest.fixture
def user_data() -> dict:
    return {
        "badge_number": None,
        "password": random_string(10),
    }


def create_user(user_data: dict, test_client: TestClient) -> dict:
    return test_client.post(USER_URL, json=user_data).json()


def login_user(user_data: dict, test_client: TestClient) -> dict:
    test_client.cookies.clear()
    test_client.headers.clear()
    login_data = {
        "username": user_data["badge_number"],
        "password": user_data["password"],
    }
    response = test_client.post(f"{USER_URL}/login", data=login_data)
    test_client.headers.update(
        {"Authorization": f"Bearer {response.json()['access_token']}"}
    )


def create_root_user():
    test_session = TestingSessionLocal()

    org_unit = OrgUnit(
        id=0,
        name="root",
    )
    test_session.add(org_unit)
    test_session.commit()

    employee = Employee(
        id=0,
        badge_number="0",
        first_name="root",
        last_name="root",
        payroll_type="hourly",
        payroll_sync=date.today(),
        workweek_type="standard",
        time_type=True,
        allow_clocking=False,
        allow_delete=False,
        org_unit_id=org_unit.id,
        manager_id=None,
        holiday_group_id=None,
    )
    test_session.add(employee)
    test_session.commit()

    user = User(
        id=0,
        badge_number=employee.badge_number,
        password=services.hash_password("password123"),
    )
    test_session.add(user)
    test_session.commit()

    auth_role = AuthRole(
        id=0,
        name="root",
        permissions=[
            AuthRolePermission(resource=resource)
            for resource in RESOURCE_SCOPES.keys()
        ],
    )
    test_session.add(auth_role)
    test_session.commit()

    auth_role_membership = AuthRoleMembership(
        auth_role_id=auth_role.id,
        user_id=user.id,
    )
    test_session.add(auth_role_membership)
    test_session.commit()

    test_session.close()


@pytest.fixture(scope="module")
def test_client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    create_root_user()

    yield test_app


@pytest.fixture(autouse=True)
def login_root_user(test_client: TestClient):
    test_client.cookies.clear()
    test_client.headers.clear()
    login_data = {"username": "0", "password": "password123"}
    response = test_client.post(f"{USER_URL}/login", data=login_data)
    test_client.headers.update(
        {"Authorization": f"Bearer {response.json()['access_token']}"}
    )

    yield
