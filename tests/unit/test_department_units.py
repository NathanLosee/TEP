from fastapi import HTTPException, status
from pytest import raises
from src.department.constants import (
    EXC_MSG_DEPARTMENT_NOT_FOUND,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_EMPLOYEE_IS_MEMBER,
    EXC_MSG_EMPLOYEE_NOT_MEMBER,
    EXC_MSG_EMPLOYEES_ASSIGNED,
)
from src.department.models import Department
from src.employee.models import Employee
import src.department.services as department_services


def test_validate_department_exists_success(department_model: Department):
    assert department_services.validate_department_exists(department_model)


def test_validate_department_exists_error_not_found():
    with raises(HTTPException) as e_info:
        department_services.validate_department_exists(None)

    assert e_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert e_info.value.detail == EXC_MSG_DEPARTMENT_NOT_FOUND


def test_validate_department_name_is_unique_success():
    assert department_services.validate_department_name_is_unique(None, 1)


def test_validate_department_name_is_unique_success_same_id(
    department_model: Department,
):
    assert department_services.validate_department_name_is_unique(
        department_model, department_model.id
    )


def test_validate_department_name_is_unique_error_name_taken(
    department_model: Department,
):
    with raises(HTTPException) as e_info:
        department_services.validate_department_name_is_unique(
            department_model, 2
        )

    assert e_info.value.status_code == status.HTTP_409_CONFLICT
    assert e_info.value.detail == EXC_MSG_NAME_ALREADY_EXISTS


def test_validate_employee_should_be_in_department_success(
    department_model: Department, employee_model: Employee
):
    department_model.employees = [employee_model]

    assert department_services.validate_department_should_have_employee(
        department_model, employee_model, True
    )


def test_validate_employee_should_be_in_department_error(
    department_model: Department, employee_model: Employee
):
    with raises(HTTPException) as e_info:
        department_services.validate_department_should_have_employee(
            department_model, employee_model, True
        )

    assert e_info.value.status_code == status.HTTP_409_CONFLICT
    assert e_info.value.detail == EXC_MSG_EMPLOYEE_NOT_MEMBER


def test_validate_employee_should_not_be_in_department_success(
    department_model: Department, employee_model: Employee
):
    assert department_services.validate_department_should_have_employee(
        department_model, employee_model, False
    )


def test_validate_employee_should_not_be_in_department_error(
    department_model: Department, employee_model: Employee
):
    department_model.employees = [employee_model]

    with raises(HTTPException) as e_info:
        department_services.validate_department_should_have_employee(
            department_model, employee_model, False
        )

    assert e_info.value.status_code == status.HTTP_409_CONFLICT
    assert e_info.value.detail == EXC_MSG_EMPLOYEE_IS_MEMBER


def test_validate_department_employees_list_is_empty_success(
    department_model: Department,
):
    department_model.employees = []

    assert department_services.validate_department_employees_list_is_empty(
        department_model
    )


def test_validate_department_employees_list_is_empty_error(
    department_model: Department, employee_model: Employee
):
    department_model.employees = [employee_model]

    with raises(HTTPException) as e_info:
        department_services.validate_department_employees_list_is_empty(
            department_model
        )

    assert e_info.value.status_code == status.HTTP_409_CONFLICT
    assert e_info.value.detail == EXC_MSG_EMPLOYEES_ASSIGNED
