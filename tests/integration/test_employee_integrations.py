from fastapi import status
from fastapi.testclient import TestClient
from src.employee.constants import BASE_URL, EXC_MSG_EMPLOYEE_NOT_FOUND
from src.employee.schemas import (
    EmployeeBase,
    EmployeeExtended,
)
from src.auth_role.constants import BASE_URL as AUTH_ROLE_URL
from src.auth_role.schemas import AuthRoleBase, AuthRoleExtended
from src.org_unit.constants import BASE_URL as ORG_UNIT_URL
from src.org_unit.schemas import OrgUnitBase, OrgUnitExtended
from src.department.constants import BASE_URL as DEPARTMENT_URL
from src.department.schemas import DepartmentBase, DepartmentExtended
from src.holiday_group.constants import BASE_URL as HOLIDAY_GROUP_URL
from src.holiday_group.schemas import (
    HolidayGroupBase,
    HolidayGroupExtended,
)


def test_create_employee_201(
    employee_base: EmployeeBase,
    employee_extended: EmployeeExtended,
    org_unit_base: OrgUnitBase,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_base.model_dump(),
    ).json()["id"]

    employee_base.org_unit_id = org_unit_id
    employee_extended.org_unit_id = org_unit_id
    response = test_client.post(
        BASE_URL,
        json=employee_base.model_dump(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == employee_extended.model_dump()


def test_get_employees_200_empty_list(
    test_client: TestClient,
):
    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_employees_200_nonempty_list(
    employee_base: EmployeeBase,
    employee_extended: EmployeeExtended,
    org_unit_base: OrgUnitBase,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_base.model_dump(),
    ).json()["id"]

    employee_base.org_unit_id = org_unit_id
    employee_extended.org_unit_id = org_unit_id
    test_client.post(
        BASE_URL,
        json=employee_base.model_dump(),
    )

    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [employee_extended.model_dump()]


def test_get_employee_200(
    employee_base: EmployeeBase,
    employee_extended: EmployeeExtended,
    org_unit_base: OrgUnitBase,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_base.model_dump(),
    ).json()["id"]

    employee_base.org_unit_id = org_unit_id
    employee_extended.org_unit_id = org_unit_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{employee_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == employee_extended.model_dump()


def test_get_employee_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.get(f"{BASE_URL}/{employee_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND


def test_get_employee_auth_roles_200(
    employee_base: EmployeeBase,
    org_unit_base: OrgUnitBase,
    auth_role_base: AuthRoleBase,
    auth_role_extended: AuthRoleExtended,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_base.model_dump(),
    ).json()["id"]

    employee_base.org_unit_id = org_unit_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    auth_role_id = test_client.post(
        AUTH_ROLE_URL,
        json=auth_role_base.model_dump(),
    ).json()["id"]
    auth_role_extended.id = auth_role_id

    test_client.post(
        f"{AUTH_ROLE_URL}/{auth_role_id}/employees/{employee_id}",
    )

    response = test_client.get(f"{BASE_URL}/{employee_id}/auth-roles")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [auth_role_extended.model_dump()]


def test_get_employee_auth_roles_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.get(f"{BASE_URL}/{employee_id}/auth-roles")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND


def test_get_employee_org_unit_200(
    employee_base: EmployeeBase,
    org_unit_base: OrgUnitBase,
    org_unit_extended: OrgUnitExtended,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_base.model_dump(),
    ).json()["id"]
    org_unit_extended.id = org_unit_id

    employee_base.org_unit_id = org_unit_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{employee_id}/org-unit")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == org_unit_extended.model_dump()


def test_get_employee_org_unit_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.get(f"{BASE_URL}/{employee_id}/org-unit")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND


def test_get_employee_departments_200(
    employee_base: EmployeeBase,
    org_unit_base: OrgUnitBase,
    department_base: DepartmentBase,
    department_extended: DepartmentExtended,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_base.model_dump(),
    ).json()["id"]

    employee_base.org_unit_id = org_unit_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    department_id = test_client.post(
        DEPARTMENT_URL,
        json=department_base.model_dump(),
    ).json()["id"]
    department_extended.id = department_id

    test_client.post(
        f"{DEPARTMENT_URL}/{department_id}/employees/{employee_id}",
    )

    response = test_client.get(f"{BASE_URL}/{employee_id}/departments")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [department_extended.model_dump()]


def test_get_employee_departments_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.get(f"{BASE_URL}/{employee_id}/departments")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND


def test_get_employee_holiday_group_200(
    employee_base: EmployeeBase,
    org_unit_base: OrgUnitBase,
    holiday_group_base: HolidayGroupBase,
    holiday_group_extended: HolidayGroupExtended,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_base.model_dump(),
    ).json()["id"]

    holiday_group_id = test_client.post(
        HOLIDAY_GROUP_URL,
        json=holiday_group_base.model_dump(),
    ).json()["id"]
    holiday_group_extended.id = holiday_group_id

    employee_base.org_unit_id = org_unit_id
    employee_base.holiday_group_id = holiday_group_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{employee_id}/holiday-group")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == holiday_group_extended.model_dump()


def test_get_employee_holiday_group_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.get(f"{BASE_URL}/{employee_id}/holiday-group")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND


def test_update_employee_200(
    employee_base: EmployeeBase,
    org_unit_base: OrgUnitBase,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_base.model_dump(),
    ).json()["id"]

    employee_base.org_unit_id = org_unit_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    employee_base.first_name = "Updated Employee Name"

    response = test_client.put(
        f"{BASE_URL}/{employee_id}",
        json=employee_base.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["first_name"] == "Updated Employee Name"


def test_update_employee_404_employee_not_found(
    employee_base: EmployeeBase,
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.put(
        f"{BASE_URL}/{employee_id}",
        json=employee_base.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND


def test_delete_employee_204(
    employee_base: EmployeeBase,
    org_unit_base: OrgUnitBase,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_base.model_dump(),
    ).json()["id"]

    employee_base.org_unit_id = org_unit_id
    employee_id = test_client.post(
        BASE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    response = test_client.delete(f"{BASE_URL}/{employee_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_employee_404_employee_not_found(
    test_client: TestClient,
):
    employee_id = 999

    response = test_client.delete(f"{BASE_URL}/{employee_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_FOUND
