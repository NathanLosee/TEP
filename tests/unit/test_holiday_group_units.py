from fastapi import HTTPException, status
from pytest import raises
from src.holiday_group.constants import (
    EXC_MSG_HOLIDAY_NAME_ALREADY_EXISTS,
    EXC_MSG_HOLIDAY_NOT_FOUND,
    EXC_MSG_HOLIDAY_GROUP_NOT_FOUND,
    EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS,
)
from src.holiday_group.models import Holiday, HolidayGroup
import src.holiday_group.services as holiday_services


def test_validate_holiday_group_exists_success(
    holiday_group_model: HolidayGroup,
):
    assert holiday_services.validate_holiday_group_exists(holiday_group_model)


def test_validate_holiday_group_exists_error_not_found():
    with raises(HTTPException) as e_info:
        holiday_services.validate_holiday_group_exists(None)

    assert e_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert e_info.value.detail == EXC_MSG_HOLIDAY_GROUP_NOT_FOUND


def test_validate_holiday_exists_success(holiday_model: Holiday):
    assert holiday_services.validate_holiday_exists(holiday_model)


def test_validate_holiday_exists_error_not_found():
    with raises(HTTPException) as e_info:
        holiday_services.validate_holiday_exists(None)

    assert e_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert e_info.value.detail == EXC_MSG_HOLIDAY_NOT_FOUND


def test_validate_holiday_group_name_is_unique_success():
    assert holiday_services.validate_holiday_group_name_is_unique(None, None)


def test_validate_holiday_group_name_is_unique_success_same_id(
    holiday_group_model: HolidayGroup,
):
    assert holiday_services.validate_holiday_group_name_is_unique(
        holiday_group_model, holiday_group_model.id
    )


def test_validate_holiday_group_name_is_unique_error_already_exists(
    holiday_group_model: HolidayGroup,
):
    with raises(HTTPException) as e_info:
        holiday_services.validate_holiday_group_name_is_unique(
            holiday_group_model, holiday_group_model.id + 1
        )

    assert e_info.value.status_code == status.HTTP_409_CONFLICT
    assert e_info.value.detail == EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS


def test_validate_holiday_name_is_unique_within_group_success():
    assert holiday_services.validate_holiday_name_is_unique_within_group(
        None, None
    )


def test_validate_holiday_name_is_unique_within_group_error_already_exists(
    holiday_model: Holiday,
):
    with raises(HTTPException) as e_info:
        holiday_services.validate_holiday_name_is_unique_within_group(
            holiday_model
        )

    assert e_info.value.status_code == status.HTTP_409_CONFLICT
    assert e_info.value.detail == EXC_MSG_HOLIDAY_NAME_ALREADY_EXISTS
