"""Module for defining patient data models.

Classes:
    - Patient: SQLAlchemy model for the 'patients' table in the database.

"""

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.encounter.models import Encounter
from src.patient.constants import (
    NAME_REGEX,
    SSN_REGEX,
    EMAIL_REGEX,
    POSTAL_REGEX,
    PERMITTED_STATE_ABBREVIATIONS_STR,
    PERMITTED_GENDER_INPUTS_STR,
)


class Patient(Base):
    """SQLAlchemy model for patient data.

    Attributes:
        id (int): Unique identifier of the patient's data in the database.
        first_name (str): First name of the patient.
        last_name (str): Last name of the patient.
        ssn (str): Social Security Number of the patient.
        email (str): Email of the patient.
        street (str): Building number and stree of the patient's address.
        city (str): City of the patient's address.
        state (str): Abbreviated state of the patient's address.
        postal (str): Zip code of the patient's address.
        age (int): Patient's age in years.
        height (int): Patient's height in inches.
        weight (int): Patient's weight in pounds.
        insurance (str): Patient's insurance provider.
        gender (str): Patient's specified gender.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    ssn: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    street: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    state: Mapped[str] = mapped_column(nullable=False)
    postal: Mapped[str] = mapped_column(nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    height: Mapped[int] = mapped_column(nullable=False)
    weight: Mapped[int] = mapped_column(nullable=False)
    insurance: Mapped[str] = mapped_column(nullable=False)
    gender: Mapped[str] = mapped_column(nullable=False)
    encounters: Mapped[list[Encounter]] = relationship(passive_deletes=True)

    __tablename__ = "patients"
    __table_args__ = (
        CheckConstraint(
            name="patients_first_name_check",
            sqltext=(f"first_name ~ '{NAME_REGEX}'"),
        ),
        CheckConstraint(
            name="patients_last_name_check",
            sqltext=(f"last_name ~ '{NAME_REGEX}'"),
        ),
        CheckConstraint(
            name="patients_ssn_check",
            sqltext=(f"ssn ~ '{SSN_REGEX}'"),
        ),
        CheckConstraint(
            name="patients_email_check",
            sqltext=f"email ~ '{EMAIL_REGEX}'",
        ),
        CheckConstraint(
            name="patients_street_check",
            sqltext="LENGTH(TRIM(street)) >= 0",
        ),
        CheckConstraint(
            name="patients_city_check",
            sqltext="LENGTH(TRIM(street)) >= 0",
        ),
        CheckConstraint(
            name="patients_state_check",
            sqltext=f"LOWER(state) in {PERMITTED_STATE_ABBREVIATIONS_STR}",
        ),
        CheckConstraint(
            name="patients_postal_check",
            sqltext=(f"postal ~ '{POSTAL_REGEX}'"),
        ),
        CheckConstraint(
            name="patients_age_check",
            sqltext="age >= 0",
        ),
        CheckConstraint(
            name="patients_height_check",
            sqltext="height >= 0",
        ),
        CheckConstraint(
            name="patients_weight_check",
            sqltext="weight >= 0",
        ),
        CheckConstraint(
            name="patients_gender_check",
            sqltext=f"LOWER(gender) in {PERMITTED_GENDER_INPUTS_STR}",
        ),
        CheckConstraint(
            name="patients_insurance_check",
            sqltext="LENGTH(TRIM(insurance)) >= 0",
        ),
    )
