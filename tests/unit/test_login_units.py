from fastapi import HTTPException, status
from pytest import raises
from src.auth_role.models import AuthRole, AuthRolePermission
from src.employee.models import Employee
from src.login.constants import EXC_MSG_LOGIN_FAILED
import src.login.services as login_services


def test_validate_login_success(employee_model: Employee):
    assert login_services.validate_login(employee_model)


def test_validate_login_error_not_found():
    with raises(HTTPException) as e_info:
        login_services.validate_login(None)

    assert e_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert e_info.value.detail == EXC_MSG_LOGIN_FAILED


def test_generate_permission_list(employee_model: Employee):
    auth_role = AuthRole(
        id=1,
        name="Admin",
        permissions=[
            AuthRolePermission(
                http_method="GET",
                resource="employee",
                restrict_to_self=False,
            )
        ],
    )
    employee_model.auth_roles = [auth_role]

    permission_list = login_services.generate_permission_list(employee_model)

    assert permission_list == [
        {
            "http_method": "GET",
            "resource": "employee",
            "restrict_to_self": False,
        }
    ]
