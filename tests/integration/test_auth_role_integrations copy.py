from fastapi import status
from fastapi.testclient import TestClient
from src.auth_role.constants import (
    BASE_URL,
    EXC_MSG_AUTH_ROLE_NOT_FOUND,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_PERMISSION_ALEADY_EXISTS,
    EXC_MSG_PERMISSION_NOT_FOUND,
    EXC_MSG_EMPLOYEE_IS_MEMBER,
    EXC_MSG_EMPLOYEE_NOT_MEMBER,
)
from src.auth_role.schemas import (
    AuthRoleBase,
    AuthRoleExtended,
    PermissionBase,
)
from src.employee.schemas import EmployeeBase
from src.employee.constants import BASE_URL as EMPLOYEE_URL
from tests.conftest import create_employee_dependencies


def test_create_auth_role_201(
    auth_role_base: AuthRoleBase,
    auth_role_extended: AuthRoleExtended,
    test_client: TestClient,
):
    response = test_client.post(url=BASE_URL, json=auth_role_base.model_dump())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == auth_role_extended.model_dump(by_alias=True)


def test_create_auth_role_409_name_already_exists(
    auth_role_base: AuthRoleBase, test_client: TestClient
):
    test_client.post(url=BASE_URL, json=auth_role_base.model_dump())

    response = test_client.post(url=BASE_URL, json=auth_role_base.model_dump())

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_NAME_ALREADY_EXISTS


def test_add_auth_role_permission_200(
    auth_role_base: AuthRoleBase,
    permission_base: PermissionBase,
    test_client: TestClient,
):
    auth_role_id = test_client.post(
        url=BASE_URL, json=auth_role_base.model_dump()
    ).json()["id"]

    response = test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/permissions",
        json=permission_base.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["permissions"]) == 1
    assert (
        response.json()["permissions"][0]["resource"]
        == permission_base.resource
    )
    assert (
        response.json()["permissions"][0]["http_method"]
        == permission_base.http_method
    )
    assert (
        response.json()["permissions"][0]["restrict_to_self"]
        == permission_base.restrict_to_self
    )


def test_add_auth_role_permission_404_auth_role_not_found(
    permission_base: PermissionBase, test_client: TestClient
):
    auth_role_id = 999

    response = test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/permissions",
        json=permission_base.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_AUTH_ROLE_NOT_FOUND


def test_add_auth_role_permission_409_permission_already_exists(
    auth_role_base: AuthRoleBase,
    permission_base: PermissionBase,
    test_client: TestClient,
):
    auth_role_id = test_client.post(
        url=BASE_URL, json=auth_role_base.model_dump()
    ).json()["id"]

    test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/permissions",
        json=permission_base.model_dump(),
    )

    response = test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/permissions",
        json=permission_base.model_dump(),
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_PERMISSION_ALEADY_EXISTS


def test_give_employee_auth_role_200(
    auth_role_base: AuthRoleBase,
    employee_base: EmployeeBase,
    test_client: TestClient,
):
    create_employee_dependencies()
    employee_id = test_client.post(
        url=EMPLOYEE_URL, json=employee_base.model_dump()
    ).json()["id"]
    auth_role_id = test_client.post(
        url=BASE_URL, json=auth_role_base.model_dump()
    ).json()["id"]

    response = test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["employees"]) == 1
    assert response.json()["employees"][0]["id"] == employee_id


def test_give_employee_auth_role_404_auth_role_not_found(
    test_client: TestClient,
):
    auth_role_id = 999
    employee_id = 999

    response = test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_AUTH_ROLE_NOT_FOUND


def test_give_employee_auth_role_409_employee_already_has_auth_role(
    auth_role_base: AuthRoleBase,
    employee_base: EmployeeBase,
    test_client: TestClient,
):
    create_employee_dependencies()
    employee_id = test_client.post(
        url=EMPLOYEE_URL, json=employee_base.model_dump()
    ).json()["id"]
    auth_role_id = test_client.post(
        url=BASE_URL, json=auth_role_base.model_dump()
    ).json()["id"]

    test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/employees/{employee_id}",
    )

    response = test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_IS_MEMBER


def test_get_auth_roles_200_empty_list(test_client: TestClient):
    response = test_client.get(url=BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_auth_roles_200_nonempty_list(
    auth_role_base: AuthRoleBase,
    auth_role_extended: AuthRoleExtended,
    test_client: TestClient,
):
    test_client.post(url=BASE_URL, json=auth_role_base.model_dump())

    response = test_client.get(url=BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [auth_role_extended.model_dump()]


def test_get_auth_role_200(
    auth_role_base: AuthRoleBase,
    auth_role_extended: AuthRoleExtended,
    test_client: TestClient,
):
    response = test_client.post(url=BASE_URL, json=auth_role_base.model_dump())
    auth_role_id = response.json()["id"]

    response = test_client.get(url=f"{BASE_URL}/{auth_role_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == auth_role_extended.model_dump()


def test_get_auth_role_404_not_found(test_client: TestClient):
    auth_role_id = 1

    response = test_client.get(url=f"{BASE_URL}/{auth_role_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_AUTH_ROLE_NOT_FOUND


def test_get_employees_by_auth_role_200_empty_list(
    auth_role_base: AuthRoleBase, test_client: TestClient
):
    auth_role_id = test_client.post(
        url=BASE_URL, json=auth_role_base.model_dump()
    ).json()["id"]

    response = test_client.get(url=f"{BASE_URL}/{auth_role_id}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_employees_by_auth_role_200_nonempty_list(
    auth_role_base: AuthRoleBase,
    employee_base: EmployeeBase,
    test_client: TestClient,
):
    create_employee_dependencies()
    employee_id = test_client.post(
        url=EMPLOYEE_URL, json=employee_base.model_dump()
    ).json()["id"]
    auth_role_id = test_client.post(
        url=BASE_URL, json=auth_role_base.model_dump()
    ).json()["id"]

    test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/employees/{employee_id}",
    )

    response = test_client.get(url=f"{BASE_URL}/{auth_role_id}/employees")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["id"] == employee_id


def test_update_auth_role_200(
    auth_role_base: AuthRoleBase,
    test_client: TestClient,
):
    response = test_client.post(url=BASE_URL, json=auth_role_base.model_dump())
    auth_role_id = response.json()["id"]

    auth_role_base.name = "Updated Auth Role"

    response = test_client.put(
        url=f"{BASE_URL}/{auth_role_id}",
        json=auth_role_base.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Updated Auth Role"


def test_update_auth_role_404_not_found(
    auth_role_base: AuthRoleBase, test_client: TestClient
):
    auth_role_id = 999

    response = test_client.put(
        url=f"{BASE_URL}/{auth_role_id}",
        json=auth_role_base.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_AUTH_ROLE_NOT_FOUND


def test_update_auth_role_409_name_already_exists(
    auth_role_base: AuthRoleBase,
    test_client: TestClient,
):
    auth_role_id = test_client.post(
        url=BASE_URL, json=auth_role_base.model_dump()
    ).json()["id"]

    auth_role_base.name = "Updated Auth Role"
    test_client.post(url=BASE_URL, json=auth_role_base.model_dump())

    response = test_client.put(
        url=f"{BASE_URL}/{auth_role_id}",
        json=auth_role_base.model_dump(),
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_NAME_ALREADY_EXISTS


def test_delete_auth_role_204(
    auth_role_base: AuthRoleBase,
    test_client: TestClient,
):
    response = test_client.post(url=BASE_URL, json=auth_role_base.model_dump())
    auth_role_id = response.json()["id"]

    response = test_client.delete(url=f"{BASE_URL}/{auth_role_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_auth_role_404_not_found(
    test_client: TestClient,
):
    auth_role_id = 999

    response = test_client.delete(url=f"{BASE_URL}/{auth_role_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_AUTH_ROLE_NOT_FOUND


def test_remove_auth_role_permission_200(
    auth_role_base: AuthRoleBase,
    permission_base: PermissionBase,
    test_client: TestClient,
):
    auth_role_id = test_client.post(
        url=BASE_URL, json=auth_role_base.model_dump()
    ).json()["id"]
    permission = test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/permissions",
        json=permission_base.model_dump(),
    ).json()["permissions"][0]

    response = test_client.delete(
        url=f"{BASE_URL}/{auth_role_id}/permissions",
        params={
            "resource": permission["resource"],
            "method": permission["http_method"],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["permissions"] == []


def test_remove_auth_role_permission_404_auth_role_not_found(
    permission_base: PermissionBase, test_client: TestClient
):
    auth_role_id = 999

    response = test_client.delete(
        url=f"{BASE_URL}/{auth_role_id}/permissions",
        params={
            "resource": permission_base.resource,
            "method": permission_base.http_method,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_AUTH_ROLE_NOT_FOUND


def test_remove_auth_role_permission_404_permission_not_found(
    auth_role_base: AuthRoleBase,
    permission_base: PermissionBase,
    test_client: TestClient,
):
    auth_role_id = test_client.post(
        url=BASE_URL, json=auth_role_base.model_dump()
    ).json()["id"]

    response = test_client.delete(
        url=f"{BASE_URL}/{auth_role_id}/permissions",
        params={
            "resource": permission_base.resource,
            "method": permission_base.http_method,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_PERMISSION_NOT_FOUND


def test_remove_auth_role_from_employee_200(
    auth_role_base: AuthRoleBase,
    employee_base: EmployeeBase,
    test_client: TestClient,
):
    employee_id = test_client.post(
        url=EMPLOYEE_URL, json=employee_base.model_dump()
    ).json()["id"]
    auth_role_id = test_client.post(
        url=BASE_URL, json=auth_role_base.model_dump()
    ).json()["id"]

    test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/employees/{employee_id}",
    )

    response = test_client.delete(
        url=f"{BASE_URL}/{auth_role_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["employees"] == []


def test_remove_auth_role_from_employee_404_auth_role_not_found(
    test_client: TestClient,
):
    auth_role_id = 999
    employee_id = 999

    response = test_client.delete(
        url=f"{BASE_URL}/{auth_role_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_AUTH_ROLE_NOT_FOUND


def test_remove_auth_role_from_employee_404_employee_not_member(
    auth_role_base: AuthRoleBase, test_client: TestClient
):
    auth_role_id = test_client.post(
        url=BASE_URL, json=auth_role_base.model_dump()
    ).json()["id"]
    employee_id = 999

    response = test_client.delete(
        url=f"{BASE_URL}/{auth_role_id}/employees/{employee_id}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_MEMBER
