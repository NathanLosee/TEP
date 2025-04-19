from fastapi import HTTPException, status
from pytest import raises
from src.org_unit.constants import (
    EXC_MSG_ORG_NOT_FOUND,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_EMPLOYEES_ASSIGNED,
)
from src.org_unit.models import OrgUnit
import src.org_unit.services as org_unit_services


def test_validate_org_unit_exists_success(org_unit_model: OrgUnit):
    assert org_unit_services.validate_org_unit_exists(org_unit_model)


def test_validate_org_unit_exists_error_not_found():
    with raises(HTTPException) as exc_info:
        org_unit_services.validate_org_unit_exists(None)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == EXC_MSG_ORG_NOT_FOUND


def test_validate_org_unit_name_is_unique_success():
    assert org_unit_services.validate_org_unit_name_is_unique(None, None)


def test_validate_org_unit_name_is_unique_success_same_id(
    org_unit_model: OrgUnit,
):
    assert org_unit_services.validate_org_unit_name_is_unique(
        org_unit_model, 1
    )


def test_validate_org_unit_name_is_unique_error_already_exists(
    org_unit_model: OrgUnit,
):
    with raises(HTTPException) as exc_info:
        org_unit_services.validate_org_unit_name_is_unique(org_unit_model, 999)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == EXC_MSG_NAME_ALREADY_EXISTS


def test_validate_org_unit_employees_list_is_empty_success(
    org_unit_model: OrgUnit,
):
    assert org_unit_services.validate_org_unit_employees_list_is_empty(
        org_unit_model
    )


def test_validate_org_unit_employees_list_is_empty_error_not_empty(
    org_unit_model: OrgUnit,
):
    org_unit_model.employees = [1, 2, 3]

    with raises(HTTPException) as exc_info:
        org_unit_services.validate_org_unit_employees_list_is_empty(
            org_unit_model
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == EXC_MSG_EMPLOYEES_ASSIGNED
