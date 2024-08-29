"""Module for defining encounter data models.

Classes:
    - Encounter: SQLAlchemy model for the 'encounters' table in the database.

"""

from datetime import date
from decimal import Decimal
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base
from src.encounter.constants import (
    VISIT_CODE_REGEX,
    BILLING_CODE_REGEX,
    ICD10_REGEX,
)


class Encounter(Base):
    """SQLAlchemy model for encounter data.

    Attributes:
        id (int): Unique identifier of the encounter's data in the database.
        patient_id (int): Unique identifier of the patient for this encounter.
        notes (str | None): Care provider's notes during the encounter.
        visit_code (str): Code for the visit type of this encounter.
        provider (str): The care provider for this encounter.
        billing_code (str): Code for billing this encounter to the patient.
        icd10 (str): International Classification of Diseases code.
        total_cost (Decimal): Total cost of this encounter for the patient.
        copay (Decimal): Required out of pocket expense for patient.
        chief_complaint (str): Primary complaint for patient's encounter.
        pulse (int | None): Observed pulse of the patient for this encounter.
        systolic (int | None): Observed systolic pressure of the patient for
            this encounter.
        diastolic (int | None): Observed diastolic pressure of the patient for
            this encounter.
        encounter_date (date): The date of this encounter.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="SET NULL"), nullable=False
    )
    notes: Mapped[str] = mapped_column(nullable=True)
    visit_code: Mapped[str] = mapped_column(nullable=False)
    provider: Mapped[str] = mapped_column(nullable=False)
    billing_code: Mapped[str] = mapped_column(nullable=False)
    icd10: Mapped[str] = mapped_column(nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(
        Numeric(scale=2, asdecimal=True), nullable=False
    )
    copay: Mapped[Decimal] = mapped_column(
        Numeric(scale=2, asdecimal=True), nullable=False
    )
    chief_complaint: Mapped[str] = mapped_column(nullable=False)
    pulse: Mapped[int] = mapped_column(nullable=True)
    systolic: Mapped[int] = mapped_column(nullable=True)
    diastolic: Mapped[int] = mapped_column(nullable=True)
    encounter_date: Mapped[date] = mapped_column(nullable=False)

    __tablename__ = "encounters"
    __table_args__ = (
        CheckConstraint(
            name="encounters_visit_code_check",
            sqltext=f"visit_code ~ '{VISIT_CODE_REGEX}'",
        ),
        CheckConstraint(
            name="encounters_provider_check",
            sqltext="LENGTH(TRIM(provider)) >= 0",
        ),
        CheckConstraint(
            name="encounters_billing_code_check",
            sqltext=f"billing_code ~ '{BILLING_CODE_REGEX}'",
        ),
        CheckConstraint(
            name="encounters_icd10_check",
            sqltext=f"icd10 ~ '{ICD10_REGEX}'",
        ),
        CheckConstraint(
            name="encounters_total_cost_check",
            sqltext="total_cost >= 0",
        ),
        CheckConstraint(
            name="encounters_copay_check",
            sqltext="copay >= 0",
        ),
        CheckConstraint(
            name="encounters_chief_complaint_check",
            sqltext="LENGTH(TRIM(chief_complaint)) >= 0",
        ),
        CheckConstraint(
            name="encounters_pulse_check",
            sqltext="pulse >= 0 OR pulse IS NULL",
        ),
        CheckConstraint(
            name="encounters_systolic_check",
            sqltext="systolic >= 0 OR systolic IS NULL",
        ),
        CheckConstraint(
            name="encounters_diastolic_check",
            sqltext="diastolic >= 0 OR diastolic IS NULL",
        ),
    )
