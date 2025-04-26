from fastapi import status
from fastapi.testclient import TestClient
from src.employee.constants import BASE_URL as EMPLOYEE_URL
from src.employee.schemas import EmployeeBase, EmployeeExtended
from src.org_unit.constants import (
    BASE_URL,
    EXC_MSG_ORG_NOT_FOUND,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_EMPLOYEES_ASSIGNED,
)
from src.org_unit.schemas import (
    OrgUnitBase,
    OrgUnitExtended,
)


def test_create_org_unit_201(
    org_unit_base: OrgUnitBase,
    org_unit_extended: OrgUnitExtended,
    test_client: TestClient,
):
    response = test_client.post(
        BASE_URL,
        json=org_unit_base.model_dump(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == org_unit_extended.model_dump()


def test_create_org_unit_409_name_already_exists(
    org_unit_base: OrgUnitBase, test_client: TestClient
):
    test_client.post(BASE_URL, json=org_unit_base.model_dump())

    response = test_client.post(
        BASE_URL,
        json=org_unit_base.model_dump(),
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": EXC_MSG_NAME_ALREADY_EXISTS}


def test_get_org_units_200_empty_list(test_client: TestClient):
    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_org_units_200_nonempty_list(
    org_unit_base: OrgUnitBase,
    org_unit_extended: OrgUnitExtended,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=org_unit_base.model_dump())

    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [org_unit_extended.model_dump()]


def test_get_org_unit_200(
    org_unit_base: OrgUnitBase,
    org_unit_extended: OrgUnitExtended,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        BASE_URL, json=org_unit_base.model_dump()
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{org_unit_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == org_unit_extended.model_dump()


def test_get_org_unit_404_not_found(
    test_client: TestClient,
):
    org_unit_id = 999

    response = test_client.get(f"{BASE_URL}/{org_unit_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_ORG_NOT_FOUND}


def test_get_employees_by_org_unit_200_empty_list(
    org_unit_base: OrgUnitBase, test_client: TestClient
):
    org_unit_id = test_client.post(
        BASE_URL, json=org_unit_base.model_dump()
    ).json()["id"]

    response = test_client.get(f"{BASE_URL}/{org_unit_id}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_employees_by_org_unit_200_nonempty_list(
    org_unit_base: OrgUnitBase,
    employee_base: EmployeeBase,
    employee_extended: EmployeeExtended,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        BASE_URL, json=org_unit_base.model_dump()
    ).json()["id"]
    employee_base.org_unit_id = org_unit_id
    employee_extended.org_unit_id = org_unit_id
    test_client.post(EMPLOYEE_URL, json=employee_base.model_dump()).json()[
        "id"
    ]

    response = test_client.get(f"{BASE_URL}/{org_unit_id}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [employee_extended.model_dump()]


def test_get_employees_by_org_unit_404_not_found(
    test_client: TestClient,
):
    org_unit_id = 999

    response = test_client.get(f"{BASE_URL}/{org_unit_id}/employees")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_ORG_NOT_FOUND}


def test_update_org_unit_200(
    org_unit_base: OrgUnitBase,
    org_unit_extended: OrgUnitExtended,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        BASE_URL, json=org_unit_base.model_dump()
    ).json()["id"]

    org_unit_extended.name = "Updated Org Unit Name"

    response = test_client.put(
        f"{BASE_URL}/{org_unit_id}",
        json=org_unit_extended.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == org_unit_extended.model_dump()


def test_update_org_unit_404_not_found(
    org_unit_base: OrgUnitBase,
    test_client: TestClient,
):
    org_unit_id = 999

    response = test_client.put(
        f"{BASE_URL}/{org_unit_id}",
        json=org_unit_base.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_ORG_NOT_FOUND}


def test_update_org_unit_409_name_already_exists(
    org_unit_base: OrgUnitBase,
    org_unit_extended: OrgUnitExtended,
    test_client: TestClient,
):
    test_client.post(BASE_URL, json=org_unit_base.model_dump())

    org_unit_id = test_client.post(
        BASE_URL, json=org_unit_base.model_dump()
    ).json()["id"]

    response = test_client.put(
        f"{BASE_URL}/{org_unit_id}",
        json=org_unit_extended.model_dump(),
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": EXC_MSG_NAME_ALREADY_EXISTS}


def test_delete_org_unit_200(
    org_unit_base: OrgUnitBase,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        BASE_URL, json=org_unit_base.model_dump()
    ).json()["id"]

    response = test_client.delete(f"{BASE_URL}/{org_unit_id}")

    assert response.status_code == status.HTTP_200_OK


def test_delete_org_unit_404_not_found(
    test_client: TestClient,
):
    org_unit_id = 999

    response = test_client.delete(f"{BASE_URL}/{org_unit_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": EXC_MSG_ORG_NOT_FOUND}


def test_delete_org_unit_409_employees_assigned(
    org_unit_base: OrgUnitBase,
    employee_base: EmployeeBase,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        BASE_URL, json=org_unit_base.model_dump()
    ).json()["id"]
    employee_base.org_unit_id = org_unit_id
    test_client.post(EMPLOYEE_URL, json=employee_base.model_dump())

    response = test_client.delete(f"{BASE_URL}/{org_unit_id}")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": EXC_MSG_EMPLOYEES_ASSIGNED}
