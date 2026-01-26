"""Database models for the license server."""

from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class License(Base):
    """License model for storing issued licenses.

    Attributes:
        id: Primary key.
        license_key: The unique license key issued to the customer.
        customer_name: Optional customer name for reference.
        created_at: When the license was created/issued.
        is_active: Whether this license is still valid.
        notes: Optional notes about this license.
    """

    __tablename__ = "licenses"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    license_key: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    customer_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    notes: Mapped[Optional[str]] = mapped_column(nullable=True)


class Activation(Base):
    """Activation model for storing license activations.

    Each license can have multiple activations (for different machines).
    The activation_key is the signed machine_id that proves the license
    is valid for that specific machine.

    Attributes:
        id: Primary key.
        license_id: Foreign key to the license.
        machine_id: The machine's unique identifier (hashed).
        activation_key: The cryptographic signature proving validity.
        activated_at: When the activation occurred.
        is_active: Whether this activation is still valid.
        deactivated_at: When the activation was revoked (if applicable).
    """

    __tablename__ = "activations"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    license_id: Mapped[int] = mapped_column(nullable=False, index=True)
    machine_id: Mapped[str] = mapped_column(nullable=False, index=True)
    activation_key: Mapped[str] = mapped_column(nullable=False)
    activated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    deactivated_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
