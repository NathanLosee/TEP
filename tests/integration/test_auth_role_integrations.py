from fastapi import status
from fastapi.testclient import TestClient

from src.auth_role.constants import (
    BASE_URL,
    EXC_MSG_AUTH_ROLE_NOT_FOUND,
    EXC_MSG_EMPLOYEE_IS_MEMBER,
    EXC_MSG_EMPLOYEE_NOT_MEMBER,
    EXC_MSG_INVALID_RESOURCE,
    EXC_MSG_NAME_ALREADY_EXISTS,
)
from src.employee.constants import BASE_URL as EMPLOYEE_URL
from src.org_unit.constants import BASE_URL as ORG_UNIT_URL
from src.user.constants import BASE_URL as USER_URL


def test_create_auth_role_201(
    auth_role_data: dict,
    test_client: TestClient,
):
    response = test_client.post(url=BASE_URL, json=auth_role_data)

    auth_role_data["id"] = response.json()["id"]

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == auth_role_data


def test_create_auth_role_400_invalid_resource(
    auth_role_data: dict,
    test_client: TestClient,
):
    auth_role_data["permissions"].append({"resource": "invalid.resource"})
    response = test_client.post(url=BASE_URL, json=auth_role_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == EXC_MSG_INVALID_RESOURCE


def test_create_auth_role_409_name_already_exists(
    auth_role_data: dict, test_client: TestClient
):
    test_client.post(url=BASE_URL, json=auth_role_data)

    response = test_client.post(url=BASE_URL, json=auth_role_data)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_NAME_ALREADY_EXISTS


def test_give_employee_auth_role_201(
    auth_role_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        url=ORG_UNIT_URL, json=org_unit_data
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        url=EMPLOYEE_URL, json=employee_data
    ).json()["id"]

    user_data["id"] = employee_id
    test_client.post(url=USER_URL, json=user_data)

    auth_role_id = test_client.post(
        url=BASE_URL,
        json=auth_role_data,
    ).json()["id"]

    response = test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/users/{employee_id}",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == [{"id": employee_id}]


def test_give_employee_auth_role_404_auth_role_not_found(
    test_client: TestClient,
):
    auth_role_id = 999
    employee_id = 999

    response = test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/users/{employee_id}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_AUTH_ROLE_NOT_FOUND


def test_give_employee_auth_role_409_employee_already_has_auth_role(
    auth_role_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        url=ORG_UNIT_URL, json=org_unit_data
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        url=EMPLOYEE_URL, json=employee_data
    ).json()["id"]

    user_data["id"] = employee_id
    test_client.post(url=USER_URL, json=user_data)

    auth_role_id = test_client.post(
        url=BASE_URL,
        json=auth_role_data,
    ).json()["id"]

    test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/users/{employee_id}",
    )

    response = test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/users/{employee_id}",
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_IS_MEMBER


def test_get_auth_roles_200(
    auth_role_data: dict,
    test_client: TestClient,
):
    auth_role_id = test_client.post(
        url=BASE_URL,
        json=auth_role_data,
    ).json()["id"]

    response = test_client.get(url=BASE_URL)

    auth_role_data["id"] = auth_role_id
    assert response.status_code == status.HTTP_200_OK
    assert auth_role_data in response.json()


def test_get_auth_role_200(
    auth_role_data: dict,
    test_client: TestClient,
):
    auth_role_id = test_client.post(
        url=BASE_URL,
        json=auth_role_data,
    ).json()["id"]

    response = test_client.get(url=f"{BASE_URL}/{auth_role_id}")

    auth_role_data["id"] = auth_role_id
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == auth_role_data


def test_get_auth_role_404_not_found(test_client: TestClient):
    auth_role_id = 999

    response = test_client.get(url=f"{BASE_URL}/{auth_role_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_AUTH_ROLE_NOT_FOUND


def test_get_users_by_auth_role_200_empty_list(
    auth_role_data: dict, test_client: TestClient
):
    auth_role_id = test_client.post(
        url=BASE_URL,
        json=auth_role_data,
    ).json()["id"]

    response = test_client.get(url=f"{BASE_URL}/{auth_role_id}/users")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_users_by_auth_role_200_nonempty_list(
    auth_role_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        url=ORG_UNIT_URL, json=org_unit_data
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        url=EMPLOYEE_URL, json=employee_data
    ).json()["id"]

    user_data["id"] = employee_id
    test_client.post(url=USER_URL, json=user_data)

    auth_role_id = test_client.post(
        url=BASE_URL,
        json=auth_role_data,
    ).json()["id"]

    test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/users/{employee_id}",
    )

    response = test_client.get(url=f"{BASE_URL}/{auth_role_id}/users")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["id"] == employee_id


def test_update_auth_role_200(
    auth_role_data: dict,
    test_client: TestClient,
):
    auth_role_id = test_client.post(
        url=BASE_URL,
        json=auth_role_data,
    ).json()["id"]

    auth_role_data["id"] = auth_role_id
    auth_role_data["name"] = "Updated Auth Role"
    response = test_client.put(
        url=f"{BASE_URL}/{auth_role_id}",
        json=auth_role_data,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == auth_role_data


def test_update_auth_role_200_add_permission(
    auth_role_data: dict,
    test_client: TestClient,
):
    auth_role_id = test_client.post(
        url=BASE_URL,
        json=auth_role_data,
    ).json()["id"]

    auth_role_data["id"] = auth_role_id
    auth_role_data["permissions"].append({"resource": "employee.create"})
    response = test_client.put(
        url=f"{BASE_URL}/{auth_role_id}",
        json=auth_role_data,
    )

    assert response.status_code == status.HTTP_200_OK
    response_permissions = sorted(
        response.json()["permissions"], key=lambda x: x["resource"]
    )
    data_permissions = sorted(
        auth_role_data["permissions"], key=lambda x: x["resource"]
    )
    assert response_permissions == data_permissions


def test_update_auth_role_200_remove_permission(
    auth_role_data: dict,
    test_client: TestClient,
):
    auth_role_id = test_client.post(url=BASE_URL, json=auth_role_data).json()[
        "id"
    ]

    auth_role_data["id"] = auth_role_id
    auth_role_data["permissions"].pop(0)

    response = test_client.put(
        url=f"{BASE_URL}/{auth_role_id}",
        json=auth_role_data,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == auth_role_data


def test_update_auth_role_404_not_found(
    auth_role_data: dict, test_client: TestClient
):
    auth_role_id = 999
    auth_role_data["id"] = auth_role_id

    response = test_client.put(
        url=f"{BASE_URL}/{auth_role_id}",
        json=auth_role_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_AUTH_ROLE_NOT_FOUND


def test_update_auth_role_409_name_already_exists(
    auth_role_data: dict,
    test_client: TestClient,
):
    auth_role_id = test_client.post(
        url=BASE_URL,
        json=auth_role_data,
    ).json()["id"]

    auth_role_data["name"] = "Updated Auth Role"
    test_client.post(url=BASE_URL, json=auth_role_data)

    auth_role_data["id"] = auth_role_id
    response = test_client.put(
        url=f"{BASE_URL}/{auth_role_id}",
        json=auth_role_data,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_NAME_ALREADY_EXISTS


def test_delete_auth_role_204(
    auth_role_data: dict,
    test_client: TestClient,
):
    response = test_client.post(url=BASE_URL, json=auth_role_data)
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


def test_remove_auth_role_from_employee_200(
    auth_role_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        url=ORG_UNIT_URL, json=org_unit_data
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        url=EMPLOYEE_URL, json=employee_data
    ).json()["id"]

    user_data["id"] = employee_id
    test_client.post(url=USER_URL, json=user_data)

    auth_role_id = test_client.post(
        url=BASE_URL,
        json=auth_role_data,
    ).json()["id"]

    test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/users/{employee_id}",
    )

    response = test_client.delete(
        url=f"{BASE_URL}/{auth_role_id}/users/{employee_id}",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_remove_auth_role_from_employee_404_auth_role_not_found(
    test_client: TestClient,
):
    auth_role_id = 999
    employee_id = 999

    response = test_client.delete(
        url=f"{BASE_URL}/{auth_role_id}/users/{employee_id}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_AUTH_ROLE_NOT_FOUND


def test_remove_auth_role_from_employee_404_employee_not_member(
    auth_role_data: dict,
    org_unit_data: dict,
    employee_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit_id = test_client.post(
        url=ORG_UNIT_URL, json=org_unit_data
    ).json()["id"]

    employee_data["org_unit_id"] = org_unit_id
    employee_id = test_client.post(
        url=EMPLOYEE_URL, json=employee_data
    ).json()["id"]

    user_data["id"] = employee_id
    test_client.post(url=USER_URL, json=user_data)

    auth_role_id = test_client.post(
        url=BASE_URL,
        json=auth_role_data,
    ).json()["id"]

    response = test_client.delete(
        url=f"{BASE_URL}/{auth_role_id}/users/{employee_id}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_EMPLOYEE_NOT_MEMBER
