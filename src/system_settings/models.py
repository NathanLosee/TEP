"""SQLAlchemy models for system settings."""

from sqlalchemy import Column, Integer, LargeBinary, String

from src.database import Base


class SystemSettings(Base):
    """System settings model for storing application configuration.

    Only one row should exist in this table (singleton pattern).

    Attributes:
        id: Primary key (always 1).
        primary_color: Primary theme color in hex format (e.g., #673AB7).
        secondary_color: Secondary theme color in hex format.
        accent_color: Accent theme color in hex format.
        logo_data: Binary data of the uploaded logo image.
        logo_mime_type: MIME type of the logo (e.g., image/png).
        logo_filename: Original filename of the uploaded logo.
        company_name: Company name to display in the application.

    """

    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, default=1)
    primary_color = Column(String(7), default="#02E600")  # --sys-primary
    secondary_color = Column(String(7), default="#BBCBB2")  # --sys-secondary
    accent_color = Column(String(7), default="#CDCD00")  # --sys-tertiary
    logo_data = Column(LargeBinary, nullable=True)
    logo_mime_type = Column(String(50), nullable=True)
    logo_filename = Column(String(255), nullable=True)
    company_name = Column(String(255), default="TEP Timeclock")
