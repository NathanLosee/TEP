from fastapi import status
from fastapi.testclient import TestClient

from src.auth_role.constants import (
    BASE_URL,
    EXC_MSG_AUTH_ROLE_NOT_FOUND,
    EXC_MSG_INVALID_RESOURCE,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_USER_IS_MEMBER,
    EXC_MSG_USER_NOT_MEMBER,
    EXC_MSG_USERS_ASSIGNED,
)
from tests.conftest import (
    chosen_auth_role_names,
    create_auth_role,
    create_auth_role_membership,
    create_employee,
    create_org_unit,
    create_user,
    random_string,
)


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
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["id"] = employee["id"]
    user = create_user(user_data, test_client)
    auth_role = create_auth_role(auth_role_data, test_client)

    response = test_client.post(
        url=f"{BASE_URL}/{auth_role["id"]}/users/{user["id"]}",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == [{"id": user["id"]}]


def test_give_employee_auth_role_404_auth_role_not_found(
    test_client: TestClient,
):
    auth_role_id = 999
    user_id = 999

    response = test_client.post(
        url=f"{BASE_URL}/{auth_role_id}/users/{user_id}",
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
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["id"] = employee["id"]
    user = create_user(user_data, test_client)
    auth_role = create_auth_role(auth_role_data, test_client)
    create_auth_role_membership(auth_role["id"], user["id"], test_client)

    response = test_client.post(
        url=f"{BASE_URL}/{auth_role["id"]}/users/{user["id"]}",
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_USER_IS_MEMBER


def test_get_auth_roles_200(
    auth_role_data: dict,
    test_client: TestClient,
):
    auth_role = create_auth_role(auth_role_data, test_client)

    response = test_client.get(url=BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert auth_role in response.json()


def test_get_auth_role_by_id_200(
    auth_role_data: dict,
    test_client: TestClient,
):
    auth_role = create_auth_role(auth_role_data, test_client)

    response = test_client.get(url=f"{BASE_URL}/{auth_role["id"]}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == auth_role


def test_get_auth_role_by_id_404_not_found(test_client: TestClient):
    auth_role_id = 999

    response = test_client.get(url=f"{BASE_URL}/{auth_role_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_AUTH_ROLE_NOT_FOUND


def test_get_users_by_auth_role_200_empty_list(
    auth_role_data: dict,
    test_client: TestClient,
):
    auth_role = create_auth_role(auth_role_data, test_client)

    response = test_client.get(url=f"{BASE_URL}/{auth_role["id"]}/users")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_users_by_auth_role_200_nonempty_list(
    auth_role_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["id"] = employee["id"]
    user = create_user(user_data, test_client)
    auth_role = create_auth_role(auth_role_data, test_client)
    create_auth_role_membership(auth_role["id"], user["id"], test_client)

    response = test_client.get(url=f"{BASE_URL}/{auth_role["id"]}/users")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["id"] == user["id"]


def test_update_auth_role_by_id_200(
    auth_role_data: dict,
    test_client: TestClient,
):
    new_name = random_string(10)
    while new_name in chosen_auth_role_names:
        new_name = random_string(10)
    chosen_auth_role_names.append(new_name)

    auth_role = create_auth_role(auth_role_data, test_client)
    auth_role["name"] = new_name

    response = test_client.put(
        url=f"{BASE_URL}/{auth_role["id"]}",
        json=auth_role,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == auth_role


def test_update_auth_role_by_id_200_add_permission(
    auth_role_data: dict,
    test_client: TestClient,
):
    auth_role = create_auth_role(auth_role_data, test_client)
    auth_role["permissions"].append({"resource": "employee.create"})

    response = test_client.put(
        url=f"{BASE_URL}/{auth_role["id"]}",
        json=auth_role,
    )

    assert response.status_code == status.HTTP_200_OK
    response_permissions = sorted(
        response.json()["permissions"], key=lambda x: x["resource"]
    )
    data_permissions = sorted(
        auth_role["permissions"], key=lambda x: x["resource"]
    )
    assert response_permissions == data_permissions


def test_update_auth_role_by_id_200_remove_permission(
    auth_role_data: dict,
    test_client: TestClient,
):
    auth_role = create_auth_role(auth_role_data, test_client)
    auth_role["permissions"].pop(0)

    response = test_client.put(
        url=f"{BASE_URL}/{auth_role["id"]}",
        json=auth_role,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == auth_role


def test_update_auth_role_by_id_404_not_found(
    auth_role_data: dict,
    test_client: TestClient,
):
    auth_role_id = 999
    auth_role_data["id"] = auth_role_id

    response = test_client.put(
        url=f"{BASE_URL}/{auth_role_id}",
        json=auth_role_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_AUTH_ROLE_NOT_FOUND


def test_update_auth_role_by_id_409_name_already_exists(
    auth_role_data: dict,
    test_client: TestClient,
):
    new_name = random_string(10)
    while new_name in chosen_auth_role_names:
        new_name = random_string(10)
    chosen_auth_role_names.append(new_name)

    auth_role = create_auth_role(auth_role_data, test_client)
    auth_role["name"] = new_name
    auth_role_data["name"] = new_name
    create_auth_role(auth_role_data, test_client)

    response = test_client.put(
        url=f"{BASE_URL}/{auth_role["id"]}",
        json=auth_role,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_NAME_ALREADY_EXISTS


def test_delete_auth_role_by_id_204(
    auth_role_data: dict,
    test_client: TestClient,
):
    auth_role = create_auth_role(auth_role_data, test_client)

    response = test_client.delete(url=f"{BASE_URL}/{auth_role["id"]}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_auth_role_by_id_404_not_found(
    test_client: TestClient,
):
    auth_role_id = 999

    response = test_client.delete(url=f"{BASE_URL}/{auth_role_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_AUTH_ROLE_NOT_FOUND


def test_delete_auth_role_by_id_409_employees_assigned(
    auth_role_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["id"] = employee["id"]
    user = create_user(user_data, test_client)
    auth_role = create_auth_role(auth_role_data, test_client)
    create_auth_role_membership(auth_role["id"], user["id"], test_client)

    response = test_client.delete(url=f"{BASE_URL}/{auth_role["id"]}")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_USERS_ASSIGNED


def test_remove_auth_role_from_employee_200(
    auth_role_data: dict,
    employee_data: dict,
    org_unit_data: dict,
    user_data: dict,
    test_client: TestClient,
):
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["id"] = employee["id"]
    user = create_user(user_data, test_client)
    auth_role = create_auth_role(auth_role_data, test_client)
    create_auth_role_membership(auth_role["id"], user["id"], test_client)

    response = test_client.delete(
        url=f"{BASE_URL}/{auth_role["id"]}/users/{user["id"]}",
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
    org_unit = create_org_unit(org_unit_data, test_client)
    employee_data["org_unit_id"] = org_unit["id"]
    employee = create_employee(employee_data, test_client)
    user_data["id"] = employee["id"]
    user = create_user(user_data, test_client)
    auth_role = create_auth_role(auth_role_data, test_client)

    response = test_client.delete(
        url=f"{BASE_URL}/{auth_role["id"]}/users/{user["id"]}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_USER_NOT_MEMBER
