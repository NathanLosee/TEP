import random
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import src.auth_role.repository as auth_role_repository
import src.user.repository as user_repository
from src.auth_role.constants import BASE_URL as AUTH_ROLE_URL
from src.auth_role.schemas import AuthRoleBase, PermissionBase
from src.constants import RESOURCE_SCOPES
from src.database import Base, get_db
from src.department.constants import BASE_URL as DEPARTMENT_URL
from src.employee.constants import BASE_URL as EMPLOYEE_URL
from src.event_log.constants import BASE_URL as EVENT_LOG_URL
from src.holiday_group.constants import BASE_URL as HOLIDAY_GROUP_URL
from src.main import app, settings
from src.org_unit.constants import BASE_URL as ORG_UNIT_URL
from src.timeclock.constants import BASE_URL as TIMECLOCK_URL
from src.user.constants import BASE_URL as USER_URL
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
chosen_employee_ids = []
chosen_holiday_group_names = []
chosen_org_unit_names = []


@pytest.fixture
def auth_role_data() -> dict:
    name = random_string(10)
    while name in chosen_auth_role_names:
        name = random_string(10)
    chosen_auth_role_names.append(name)

    return {
        "name": name,
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
    name = random_string(10)
    while name in chosen_department_names:
        name = random_string(10)
    chosen_department_names.append(name)

    return {
        "name": name,
    }


def create_department(department_data: dict, test_client: TestClient) -> dict:
    return test_client.post(DEPARTMENT_URL, json=department_data).json()


def create_department_membership(
    department_id: int, user_id: int, test_client: TestClient
) -> dict:
    test_client.post(f"{DEPARTMENT_URL}/{department_id}/employees/{user_id}")


@pytest.fixture
def employee_data() -> dict:
    employee_id = random.randint(2, 1000000)
    while employee_id in chosen_employee_ids:
        employee_id = random.randint(2, 1000000)
    chosen_employee_ids.append(employee_id)

    return {
        "id": employee_id,
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
        "user_id": 0,
    }


def create_event_log(event_log_data: dict, test_client: TestClient) -> dict:
    return test_client.post(EVENT_LOG_URL, json=event_log_data).json()


@pytest.fixture
def holiday_group_data() -> dict:
    name = random_string(10)
    while name in chosen_holiday_group_names:
        name = random_string(10)
    chosen_holiday_group_names.append(name)

    return {
        "name": name,
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
    name = random_string(10)
    while name in chosen_org_unit_names:
        name = random_string(10)
    chosen_org_unit_names.append(name)

    return {
        "name": name,
    }


def create_org_unit(org_unit_data: dict, test_client: TestClient) -> dict:
    return test_client.post(ORG_UNIT_URL, json=org_unit_data).json()


@pytest.fixture
def timeclock_data() -> dict:
    return {
        "id": 1,
        "employee_id": None,
        "clock_in": date.today().isoformat(),
        "clock_out": None,
    }


def clock_employee(employee_id: int, test_client: TestClient) -> dict:
    return test_client.post(f"{TIMECLOCK_URL}/{employee_id}").json()


@pytest.fixture
def user_data() -> dict:
    return {
        "id": 2,
        "password": random_string(10),
    }


def create_user(user_data: dict, test_client: TestClient) -> dict:
    return test_client.post(USER_URL, json=user_data).json()


def login_user(user_data: dict, test_client: TestClient) -> dict:
    test_client.cookies.clear()
    test_client.headers.clear()
    login_data = {
        "username": str(user_data["id"]),
        "password": user_data["password"],
    }
    response = test_client.post(f"{USER_URL}/login", data=login_data)
    test_client.headers.update(
        {"Authorization": f"Bearer {response.json()['access_token']}"}
    )


def create_root_user():
    test_session = TestingSessionLocal()

    user_data = {"id": 0, "password": "password123"}
    user_repository.create_user(UserBase(**user_data), test_session)
    auth_role_id = auth_role_repository.create_auth_role(
        AuthRoleBase(
            name="Admin",
            permissions=[
                PermissionBase(resource=resource)
                for resource in RESOURCE_SCOPES
            ],
        ),
        test_session,
    ).id
    auth_role_repository.create_membership(
        auth_role_id, user_data["id"], test_session
    )

    test_session.close()


def create_timeclock_user():
    test_session = TestingSessionLocal()

    user_data = {"id": 1, "password": "password123"}
    user_repository.create_user(UserBase(**user_data), test_session)

    test_session.close()


@pytest.fixture(scope="module")
def test_client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    create_root_user()
    create_timeclock_user()

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
