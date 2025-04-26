from fastapi import status
from fastapi.testclient import TestClient
from src.department.constants import (
    BASE_URL,
    EXC_MSG_DEPARTMENT_NOT_FOUND,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_EMPLOYEE_IS_MEMBER,
    EXC_MSG_EMPLOYEE_NOT_MEMBER,
    EXC_MSG_EMPLOYEES_ASSIGNED,
)
from src.department.schemas import (
    DepartmentBase,
    DepartmentExtended,
)
from src.employee.schemas import EmployeeBase
from src.employee.constants import BASE_URL as EMPLOYEE_URL
from src.org_unit.schemas import OrgUnitBase
from src.org_unit.constants import BASE_URL as ORG_UNIT_URL


def test_create_department_201(
    department_base: DepartmentBase,
    department_extended: DepartmentExtended,
    test_client: TestClient,
):
    response = test_client.post(
        BASE_URL,
        json=department_base.model_dump(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == department_extended.model_dump()


def test_create_department_409_name_already_exists(
    department_base: DepartmentBase,
    test_client: TestClient,
):
    test_client.post(
        BASE_URL,
        json=department_base.model_dump(),
    )

    response = test_client.post(
        BASE_URL,
        json=department_base.model_dump(),
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_NAME_ALREADY_EXISTS


def test_create_department_membership_201(
    department_base: DepartmentBase,
    employee_base: EmployeeBase,
    org_unit_base: OrgUnitBase,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_base.model_dump(),
    ).json()["id"]
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_base.model_dump(),
    ).json()["id"]
    employee_base.org_unit_id = org_unit_id
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    response = test_client.post(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert len(response.json()["employees"]) == 1
    assert response.json()["employees"][0]["id"] == employee_id


def test_create_department_membership_404_department_not_found(
    test_client: TestClient,
):
    department_id = 999
    employee_id = 999

    response = test_client.post(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_create_department_membership_409_employee_already_member(
    department_base: DepartmentBase,
    employee_base: EmployeeBase,
    org_unit_base: OrgUnitBase,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_base.model_dump(),
    ).json()["id"]
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_base.model_dump(),
    ).json()["id"]
    employee_base.org_unit_id = org_unit_id
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    test_client.post(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    response = test_client.post(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_IS_MEMBER


def test_get_departments_200_empty_list(
    test_client: TestClient,
):
    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_departments_200_nonempty_list(
    department_base: DepartmentBase,
    department_extended: DepartmentExtended,
    test_client: TestClient,
):
    test_client.post(
        BASE_URL,
        json=department_base.model_dump(),
    )

    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [department_extended.model_dump()]


def test_get_department_200(
    department_base: DepartmentBase,
    department_extended: DepartmentExtended,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_base.model_dump(),
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{department_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == department_extended.model_dump()


def test_get_department_404_department_not_found(
    test_client: TestClient,
):
    department_id = 999

    response = test_client.get(f"{BASE_URL}/{department_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_get_employees_by_department_200_empty_list(
    department_base: DepartmentBase,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_base.model_dump(),
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{department_id}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_employees_by_department_200_nonempty_list(
    department_base: DepartmentBase,
    employee_base: EmployeeBase,
    employee_extended: EmployeeBase,
    org_unit_base: OrgUnitBase,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_base.model_dump(),
    ).json()["id"]
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_base.model_dump(),
    ).json()["id"]
    employee_base.org_unit_id = org_unit_id
    employee_extended.org_unit_id = org_unit_id
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    test_client.post(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    response = test_client.get(f"{BASE_URL}/{department_id}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0] == employee_extended.model_dump()


def test_get_employees_by_department_404_department_not_found(
    test_client: TestClient,
):
    department_id = 999

    response = test_client.get(f"{BASE_URL}/{department_id}/employees")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_get_jobs_by_department_404_department_not_found(
    test_client: TestClient,
):
    department_id = 999

    response = test_client.get(f"{BASE_URL}/{department_id}/jobs")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_update_department_200(
    department_base: DepartmentBase,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_base.model_dump(),
    ).json()["id"]

    department_base.name = "Updated Department Name"

    response = test_client.put(
        f"{BASE_URL}/{department_id}",
        json=department_base.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Updated Department Name"


def test_update_department_404_department_not_found(
    department_base: DepartmentBase,
    test_client: TestClient,
):
    department_id = 999

    response = test_client.put(
        f"{BASE_URL}/{department_id}",
        json=department_base.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_update_department_409_name_already_exists(
    department_base: DepartmentBase,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_base.model_dump(),
    ).json()["id"]

    department_base.name = "Updated Department Name"
    test_client.post(
        BASE_URL,
        json=department_base.model_dump(),
    )

    response = test_client.put(
        f"{BASE_URL}/{department_id}",
        json=department_base.model_dump(),
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_NAME_ALREADY_EXISTS


def test_delete_department_204(
    department_base: DepartmentBase,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_base.model_dump(),
    ).json()["id"]

    response = test_client.delete(f"{BASE_URL}/{department_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_department_404_department_not_found(
    test_client: TestClient,
):
    department_id = 999

    response = test_client.delete(f"{BASE_URL}/{department_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_delete_department_409_employees_assigned(
    department_base: DepartmentBase,
    employee_base: EmployeeBase,
    org_unit_base: OrgUnitBase,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_base.model_dump(),
    ).json()["id"]
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_base.model_dump(),
    ).json()["id"]
    employee_base.org_unit_id = org_unit_id
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    test_client.post(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    response = test_client.delete(f"{BASE_URL}/{department_id}")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_EMPLOYEES_ASSIGNED


def test_delete_department_membership_200(
    department_base: DepartmentBase,
    employee_base: EmployeeBase,
    org_unit_base: OrgUnitBase,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_base.model_dump(),
    ).json()["id"]
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_base.model_dump(),
    ).json()["id"]
    employee_base.org_unit_id = org_unit_id
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    test_client.post(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    response = test_client.delete(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_department_membership_404_department_not_found(
    test_client: TestClient,
):
    department_id = 999
    employee_id = 999

    response = test_client.delete(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_delete_department_membership_404_employee_not_member(
    department_base: DepartmentBase,
    employee_base: EmployeeBase,
    org_unit_base: OrgUnitBase,
    test_client: TestClient,
):
    department_id = test_client.post(
        BASE_URL,
        json=department_base.model_dump(),
    ).json()["id"]
    org_unit_id = test_client.post(
        ORG_UNIT_URL,
        json=org_unit_base.model_dump(),
    ).json()["id"]
    employee_base.org_unit_id = org_unit_id
    employee_id = test_client.post(
        EMPLOYEE_URL,
        json=employee_base.model_dump(),
    ).json()["id"]

    response = test_client.delete(
        f"{BASE_URL}/{department_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_MEMBER
