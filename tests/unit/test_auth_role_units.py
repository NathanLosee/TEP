from fastapi import HTTPException, status
from pytest import raises
from src.auth_role.constants import (
    EXC_MSG_AUTH_ROLE_NOT_FOUND,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_PERMISSION_ALEADY_EXISTS,
    EXC_MSG_PERMISSION_NOT_FOUND,
    EXC_MSG_EMPLOYEE_IS_MEMBER,
    EXC_MSG_EMPLOYEE_NOT_MEMBER,
)
from src.auth_role.models import AuthRole
from src.employee.models import Employee
import src.auth_role.services as auth_role_services


def test_validate_auth_role_exists_success(auth_role_model: AuthRole):
    assert auth_role_services.validate_auth_role_exists(auth_role_model)


def test_validate_auth_role_exists_error_not_found():
    with raises(HTTPException) as e_info:
        auth_role_services.validate_auth_role_exists(None)

    assert e_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert e_info.value.detail == EXC_MSG_AUTH_ROLE_NOT_FOUND


def test_validate_auth_role_name_is_unique_success():
    assert auth_role_services.validate_auth_role_name_is_unique(None, 1)


def test_validate_auth_role_name_is_unique_success_same_id(
    auth_role_model: AuthRole,
):
    assert auth_role_services.validate_auth_role_name_is_unique(
        auth_role_model, auth_role_model.id
    )


def test_validate_auth_role_name_is_unique_error_name_taken(
    auth_role_model: AuthRole,
):
    with raises(HTTPException) as e_info:
        auth_role_services.validate_auth_role_name_is_unique(
            auth_role_model, 2
        )

    assert e_info.value.status_code == status.HTTP_409_CONFLICT
    assert e_info.value.detail == EXC_MSG_NAME_ALREADY_EXISTS


def test_validate_auth_role_permission_exists_success_should_have(
    auth_role_model: AuthRole, auth_role_permission_model: AuthRole
):
    auth_role_model.permissions = [auth_role_permission_model]

    assert auth_role_services.validate_auth_role_permission_exists(
        auth_role_model, auth_role_permission_model, True
    )


def test_validate_auth_role_permission_exists_success_should_not_have(
    auth_role_model: AuthRole, auth_role_permission_model: AuthRole
):
    assert auth_role_services.validate_auth_role_permission_exists(
        auth_role_model, auth_role_permission_model, False
    )


def test_validate_auth_role_permission_exists_error_should_have(
    auth_role_model: AuthRole, auth_role_permission_model: AuthRole
):
    with raises(HTTPException) as e_info:
        auth_role_services.validate_auth_role_permission_exists(
            auth_role_model, auth_role_permission_model, True
        )

    assert e_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert e_info.value.detail == EXC_MSG_PERMISSION_NOT_FOUND


def test_validate_auth_role_permission_exists_error_should_not_have(
    auth_role_model: AuthRole, auth_role_permission_model: AuthRole
):
    auth_role_model.permissions = [auth_role_permission_model]

    with raises(HTTPException) as e_info:
        auth_role_services.validate_auth_role_permission_exists(
            auth_role_model, auth_role_permission_model, False
        )

    assert e_info.value.status_code == status.HTTP_409_CONFLICT
    assert e_info.value.detail == EXC_MSG_PERMISSION_ALEADY_EXISTS


def test_validate_employee_should_have_auth_role_success(
    auth_role_model: AuthRole, employee_model: Employee
):
    auth_role_model.employees = [employee_model]

    assert auth_role_services.validate_employee_should_have_auth_role(
        auth_role_model, employee_model, True
    )


def test_validate_employee_should_have_auth_role_error(
    auth_role_model: AuthRole, employee_model: Employee
):
    with raises(HTTPException) as e_info:
        auth_role_services.validate_employee_should_have_auth_role(
            auth_role_model, employee_model, True
        )

    assert e_info.value.status_code == status.HTTP_409_CONFLICT
    assert e_info.value.detail == EXC_MSG_EMPLOYEE_NOT_MEMBER


def test_validate_employee_should_not_have_auth_role_success(
    auth_role_model: AuthRole, employee_model: Employee
):
    assert auth_role_services.validate_employee_should_have_auth_role(
        auth_role_model, employee_model, False
    )


def test_validate_employee_should_not_have_auth_role_error(
    auth_role_model: AuthRole, employee_model: Employee
):
    auth_role_model.employees = [employee_model]

    with raises(HTTPException) as e_info:
        auth_role_services.validate_employee_should_have_auth_role(
            auth_role_model, employee_model, False
        )

    assert e_info.value.status_code == status.HTTP_409_CONFLICT
    assert e_info.value.detail == EXC_MSG_EMPLOYEE_IS_MEMBER
