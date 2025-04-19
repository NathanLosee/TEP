from fastapi import HTTPException, status
from pytest import raises
from src.employee.constants import EXC_MSG_EMPLOYEE_NOT_FOUND
from src.employee.models import Employee
import src.employee.services as employee_services


def test_validate_employee_exists_success(employee_model: Employee):
    assert employee_services.validate_employee_exists(employee_model)


def test_validate_employee_exists_error_not_found():
    with raises(HTTPException) as e_info:
        employee_services.validate_employee_exists(None)

    assert e_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert e_info.value.detail == EXC_MSG_EMPLOYEE_NOT_FOUND
