"""Module for defining license Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LicenseActivate(BaseModel):
    """Schema for license activation request.

    Attributes:
        license_key (str): The Ed25519 signature that serves as the license key.
        server_id (str): Optional machine identifier for binding.

    """

    license_key: str = Field(..., min_length=64, max_length=256, description="Ed25519 signature in hex format")
    server_id: Optional[str] = None


class LicenseStatus(BaseModel):
    """Schema for license status response.

    Attributes:
        is_active (bool): Whether a license is currently active.
        license_key (str): The active license key if one exists.
        activated_at (datetime): When the license was activated.
        server_id (str): Machine identifier if bound.

    """

    is_active: bool
    license_key: Optional[str] = None
    activated_at: Optional[datetime] = None
    server_id: Optional[str] = None


class LicenseExtended(BaseModel):
    """Schema for extended license information.

    Attributes:
        id (int): License's unique identifier.
        license_key (str): The license key.
        activated_at (datetime): When the license was activated.
        is_active (bool): Whether the license is currently active.
        server_id (str): Optional machine identifier.

    """

    id: int
    license_key: str
    activated_at: datetime
    is_active: bool
    server_id: Optional[str] = None

    model_config = {"from_attributes": True}
