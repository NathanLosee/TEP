"""Module for defining license data models.

Classes:
    - License: SQLAlchemy model for the 'licenses' table in the database.

"""

from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.license.constants import IDENTIFIER


class License(Base):
    """SQLAlchemy model for license data.

    Attributes:
        id (int): License's unique identifier.
        license_key (str): The Ed25519 signature that serves as the license key.
        activated_at (datetime): When the license was activated.
        is_active (bool): Whether the license is currently active.
        server_id (str): Optional machine identifier for binding.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    license_key: Mapped[str] = mapped_column(
        unique=True, nullable=False, index=True
    )
    activated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    server_id: Mapped[Optional[str]] = mapped_column(nullable=True)

    __tablename__ = IDENTIFIER
