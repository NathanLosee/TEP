"""Module for defining registered browser request and response schemas.

Classes:
    - RegisteredBrowserBase: Pydantic schema for request/response data.
    - RegisteredBrowserExtended: Extended schema with id.
    - RegisteredBrowserCreate: Schema for creating new browser registration.
    - RegisteredBrowserVerify: Schema for verifying browser fingerprint.

"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RegisteredBrowserBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        browser_uuid (str): Browser's unique UUID.
        browser_name (str): Browser's friendly name.

    """

    browser_uuid: str
    browser_name: str

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)


class RegisteredBrowserCreate(RegisteredBrowserBase):
    """Schema for creating a new browser registration.

    Attributes:
        browser_uuid (Optional[str]): Browser's unique UUID
            (auto-generated if not provided).
        fingerprint_hash (str): Hash of browser fingerprint.
        user_agent (str): Browser user agent string.
        ip_address (str): IP address at registration time.

    """

    browser_uuid: Optional[str] = None  # Optional, auto-gen
    fingerprint_hash: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "browser_name": "Front Desk Kiosk",
                "browser_uuid": None,
                "fingerprint_hash": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "ip_address": "192.168.1.100",
            }
        }
    }


class RegisteredBrowserExtended(RegisteredBrowserBase):
    """Extended pydantic schema with additional fields.

    Attributes:
        id (int): Browser's unique identifier.
        fingerprint_hash (str): Hash of browser fingerprint.
        user_agent (str): Browser user agent string.
        ip_address (str): IP address at registration time.
        registered_at (datetime): When the browser was registered.
        last_seen (datetime): Last time the browser was used.
        is_active (bool): Whether the browser is currently active.

    """

    id: int
    fingerprint_hash: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    registered_at: datetime
    last_seen: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class RegisteredBrowserVerify(BaseModel):
    """Schema for verifying browser fingerprint.

    Attributes:
        fingerprint_hash (str): Hash of browser fingerprint to verify.
        browser_uuid (str): Optional UUID if browser has one stored.

    """

    fingerprint_hash: str
    browser_uuid: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "fingerprint_hash": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
                "browser_uuid": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
    }


class RegisteredBrowserRecover(BaseModel):
    """Schema for recovering browser registration with recovery code.

    Attributes:
        recovery_code (str): The recovery code (UUID) to recover registration.
        fingerprint_hash (str): Current browser fingerprint for verification.

    """

    recovery_code: str
    fingerprint_hash: str

    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_min_length=1,
        json_schema_extra={
            "example": {
                "recovery_code": "550e8400-e29b-41d4-a716-446655440000",
                "fingerprint_hash": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
            }
        },
    )
