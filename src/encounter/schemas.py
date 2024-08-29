"""Module for defining encounter request and response schemas.

Classes:
    - EncounterBase: Pydantic schema for request/response data.
    - EncounterBaseWithId: Base Pydantic schema extended with id field.

"""

from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_serializer
from src.encounter.constants import (
    VISIT_CODE_REGEX,
    BILLING_CODE_REGEX,
    ICD10_REGEX,
)


class EncounterBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        patient_id (int): Unique identifier of the patient for this encounter.
        notes (str | None): Care provider's notes during the encounter.
        visit_code (str): Code for the type of this encounter.
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

    patient_id: int
    notes: Optional[str] = Field(default=None)
    visit_code: str = Field(pattern=VISIT_CODE_REGEX)
    provider: str
    billing_code: str = Field(pattern=BILLING_CODE_REGEX)
    icd10: str = Field(pattern=ICD10_REGEX)
    total_cost: Decimal = Field(ge=0)
    copay: Decimal = Field(ge=0)
    chief_complaint: str
    pulse: Optional[int] = Field(default=None, ge=0)
    systolic: Optional[int] = Field(default=None, ge=0)
    diastolic: Optional[int] = Field(default=None, ge=0)
    encounter_date: date = Field(alias="date")

    @field_serializer("total_cost", "copay")
    def serialize_decimal(v: Decimal) -> str:
        """Serializes Decimal value into a str.

        Returns:
            str: The serialized value.

        """
        return str(v)

    @field_serializer("encounter_date")
    def serialize_date(v: date):
        """Serializes date value into a str.

        Returns:
            str: The serialized value.

        """
        return str(v)

    model_config = ConfigDict(
        str_strip_whitespace=True, str_min_length=1, populate_by_name=True
    )


class EncounterBaseWithId(EncounterBase):
    """Base Pydantic schema extended with id field.

    Attributes:
        id (int): Unique identifier of the encounter's data in the database.

    """

    id: int

    model_config = ConfigDict(from_attributes=True)
