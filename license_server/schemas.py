"""Pydantic schemas for the license server API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Request schemas
class LicenseCreate(BaseModel):
    """Schema for creating a new license."""

    customer_name: Optional[str] = None
    notes: Optional[str] = None


class ActivationRequest(BaseModel):
    """Schema for license activation request from client application."""

    license_key: str = Field(..., min_length=1, description="The license key to activate")
    machine_id: str = Field(..., min_length=1, description="The client machine's unique ID")


class DeactivationRequest(BaseModel):
    """Schema for license deactivation request."""

    license_key: str = Field(..., min_length=1, description="The license key to deactivate")
    machine_id: str = Field(..., min_length=1, description="The machine ID to deactivate")


class ValidationRequest(BaseModel):
    """Schema for validating an existing activation."""

    license_key: str = Field(..., min_length=1, description="The license key")
    machine_id: str = Field(..., min_length=1, description="The machine ID")
    activation_key: str = Field(..., min_length=1, description="The activation key to validate")


# Response schemas
class LicenseResponse(BaseModel):
    """Schema for license response."""

    id: int
    license_key: str
    customer_name: Optional[str] = None
    created_at: datetime
    is_active: bool
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class ActivationResponse(BaseModel):
    """Schema for activation response returned to client application."""

    license_key: str
    activation_key: str
    activated_at: datetime

    model_config = {"from_attributes": True}


class ValidationResponse(BaseModel):
    """Schema for validation response."""

    is_valid: bool
    message: str


class LicenseStatusResponse(BaseModel):
    """Schema for license status check response."""

    is_valid: bool
    license_key: Optional[str] = None
    activated_at: Optional[datetime] = None
    message: str
