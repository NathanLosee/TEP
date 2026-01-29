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
        license_key (str): The unique license key (hex format).
        activation_key (str): The signed proof binding license to this machine.
        activated_at (datetime): When the license was activated.
        is_active (bool): Whether the license is currently active.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    license_key: Mapped[str] = mapped_column(
        unique=True, nullable=False, index=True
    )
    activation_key: Mapped[str] = mapped_column(nullable=False)
    activated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True, index=True)

    __tablename__ = IDENTIFIER
