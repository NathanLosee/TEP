"""Module for defining encounter-level constants."""

from src.constants import CAPITALIZED_REGEX as C, DIGIT_REGEX as D

BASE_URL = "/patients/{patient_id}/encounters"
VISIT_CODE_REGEX = f"^{C}{D}{C} {D}{C}{D}$"
BILLING_CODE_REGEX = f"^{D}{{3}}.{D}{{3}}.{D}{{3}}-{D}{{2}}$"
ICD10_REGEX = f"^{C}{D}{{2}}$"
EXCEPTION_MESSAGE_ENCOUNTER_NOT_FOUND = "Encounter does not exist."
EXCEPTION_MESSAGE_ENCOUNTER_NOT_FOR_PATIENT = (
    "Encounter does not involve the referenced patient."
)
