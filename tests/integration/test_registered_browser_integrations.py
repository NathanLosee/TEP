import uuid

from fastapi import status
from fastapi.testclient import TestClient

from src.registered_browser.constants import BASE_URL, EXC_MSG_BROWSER_NOT_FOUND


def test_register_browser_201(test_client: TestClient):
    """Test successfully registering a new browser."""
    browser_uuid = str(uuid.uuid4())
    response = test_client.post(
        BASE_URL,
        json={"browser_uuid": browser_uuid, "browser_name": "Test Browser"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert "browser_uuid" in response.json()
    assert response.json()["browser_uuid"] == browser_uuid
    assert response.json()["browser_name"] == "Test Browser"
    assert "id" in response.json()


def test_register_browser_409_already_registered(test_client: TestClient):
    """Test registering the same browser twice returns 409."""
    browser_uuid = str(uuid.uuid4())
    test_client.post(
        BASE_URL,
        json={"browser_uuid": browser_uuid, "browser_name": "Test Browser"},
    )

    # Try to register again
    response = test_client.post(
        BASE_URL,
        json={"browser_uuid": browser_uuid, "browser_name": "Test Browser"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "detail" in response.json()


def test_get_registered_browsers_200(test_client: TestClient):
    """Test retrieving all registered browsers."""
    # Register a browser first
    browser_uuid = str(uuid.uuid4())
    test_client.post(
        BASE_URL,
        json={"browser_uuid": browser_uuid, "browser_name": "Test Browser"},
    )

    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    # Check that our registered browser is in the list
    uuids = [browser["browser_uuid"] for browser in response.json()]
    assert browser_uuid in uuids


def test_delete_registered_browser_204(test_client: TestClient):
    """Test successfully deleting a registered browser."""
    # Register a browser first
    browser_uuid = str(uuid.uuid4())
    register_response = test_client.post(
        BASE_URL,
        json={"browser_uuid": browser_uuid, "browser_name": "Test Browser"},
    )
    browser_id = register_response.json()["id"]

    response = test_client.delete(f"{BASE_URL}/{browser_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify browser is deleted
    get_response = test_client.get(BASE_URL)
    uuids = [browser["browser_uuid"] for browser in get_response.json()]
    assert browser_uuid not in uuids


def test_delete_registered_browser_404_not_found(test_client: TestClient):
    """Test deleting a non-existent browser returns 404."""
    fake_id = 999999

    response = test_client.delete(f"{BASE_URL}/{fake_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_BROWSER_NOT_FOUND
