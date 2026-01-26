"""Module for defining license Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LicenseActivate(BaseModel):
    """Schema for license activation request.

    The user enters a license_key, and the backend contacts the license
    server to get an activation_key for this machine.

    Attributes:
        license_key (str): The unique license key (word or hex format).

    """

    license_key: str = Field(
        ..., min_length=64, description="License key in word or hex format"
    )


class LicenseStatus(BaseModel):
    """Schema for license status response.

    Attributes:
        is_active (bool): Whether a license is currently active.
        license_key (str): The active license key if one exists.
        activated_at (datetime): When the license was activated.
        needs_reactivation (bool): True if a license exists but needs re-activation.

    """

    is_active: bool
    license_key: Optional[str] = None
    activated_at: Optional[datetime] = None
    needs_reactivation: bool = False


class LicenseExtended(BaseModel):
    """Schema for extended license information.

    Attributes:
        id (int): License's unique identifier.
        license_key (str): The license key.
        activation_key (str): The signed activation key.
        activated_at (datetime): When the license was activated.
        is_active (bool): Whether the license is currently active.

    """

    id: int
    license_key: str
    activation_key: str
    activated_at: datetime
    is_active: bool

    model_config = {"from_attributes": True}
