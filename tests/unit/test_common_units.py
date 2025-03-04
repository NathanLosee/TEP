from fastapi import HTTPException, status
from pytest import raises
from src.constants import EXC_MSG_IDS_DO_NOT_MATCH
import src.services as common_services


def test_validate_ids_match_success():
    body_id = 1
    path_id = 1

    assert common_services.validate_ids_match(body_id, path_id)


def test_validate_ids_match_error_not_match():
    body_id = 1
    path_id = 0

    with raises(HTTPException) as e_info:
        common_services.validate_ids_match(body_id, path_id)

    assert e_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert e_info.value.detail == EXC_MSG_IDS_DO_NOT_MATCH
