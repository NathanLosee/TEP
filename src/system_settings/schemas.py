"""Pydantic schemas for system settings request/response validation."""

import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator


def validate_hex_color(value: Optional[str]) -> Optional[str]:
    """Validate hex color format."""
    if value is None:
        return value
    if not re.match(r"^#[0-9A-Fa-f]{6}$", value):
        raise ValueError("Invalid hex color format. Expected format: #RRGGBB")
    return value.upper()


class SystemSettingsBase(BaseModel):
    """Base schema for system settings.

    Attributes:
        primary_color: Primary theme color in hex format.
        secondary_color: Secondary theme color in hex format.
        accent_color: Accent theme color in hex format.
        company_name: Company name to display.

    """

    primary_color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary_color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    accent_color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    company_name: Optional[str] = Field(None, max_length=255)

    @field_validator("primary_color", "secondary_color", "accent_color", mode="before")
    @classmethod
    def validate_colors(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize hex colors."""
        return validate_hex_color(v)


class SystemSettingsUpdate(SystemSettingsBase):
    """Schema for updating system settings."""

    pass


class SystemSettingsResponse(BaseModel):
    """Schema for system settings response.

    Attributes:
        id: Settings ID (always 1).
        primary_color: Primary theme color.
        secondary_color: Secondary theme color.
        accent_color: Accent theme color.
        company_name: Company name.
        has_logo: Whether a logo has been uploaded.
        logo_filename: Original filename of the logo.

    """

    id: int
    primary_color: str
    secondary_color: str
    accent_color: str
    company_name: str
    has_logo: bool = False
    logo_filename: Optional[str] = None

    model_config = {"from_attributes": True}
