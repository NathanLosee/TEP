"""Module for defining patient request and response schemas.

Classes:
    - PatientBase: Pydantic schema for request/response data.
    - PatientBaseWithId: Base Pydantic schema extended with id field.

"""

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)
from src.patient.constants import (
    NAME_REGEX,
    SSN_REGEX,
    POSTAL_REGEX,
    PERMITTED_STATE_ABBREVIATIONS,
    PERMITTED_GENDER_INPUTS,
    EXCEPTION_MESSAGE_STATE_NOT_VALID,
    EXCEPTION_MESSAGE_GENDER_INPUT_NOT_VALID,
)


class PatientBase(BaseModel):
    """Pydantic schema for request/response data.

    Attributes:
        first_name (str): First name of the patient.
        last_name (str): Last name of the patient.
        ssn (str): Social Security Number of the patient.
        email (EmailStr): Email of the patient.
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

    first_name: str = Field(pattern=NAME_REGEX)
    last_name: str = Field(pattern=NAME_REGEX)
    ssn: str = Field(pattern=SSN_REGEX)
    email: EmailStr
    street: str
    city: str
    state: str
    postal: str = Field(pattern=POSTAL_REGEX)
    age: int = Field(ge=0)
    height: int = Field(ge=0)
    weight: int = Field(ge=0)
    insurance: str
    gender: str

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    @field_validator("state")
    @classmethod
    def validate_state_is_permitted(cls, value: str) -> str:
        """Validates the state value is within the permitted list.

        Args:
            value (str): The state value to check.

        Raises:
            ValueError: If state value is not in permitted list.

        Returns:
            str: The state value.

        """
        if value.lower() not in PERMITTED_STATE_ABBREVIATIONS:
            raise ValueError(EXCEPTION_MESSAGE_STATE_NOT_VALID)
        return value

    @field_validator("gender")
    @classmethod
    def validate_gender_is_permitted(cls, value: str) -> str:
        """Validates the gender value is within the permitted list.

        Args:
            value (str): The gender value to check.

        Raises:
            ValueError: If gender value is not in permitted list.

        Returns:
            str: The gender value.

        """
        if value.lower() not in PERMITTED_GENDER_INPUTS:
            raise ValueError(EXCEPTION_MESSAGE_GENDER_INPUT_NOT_VALID)
        return value


class PatientBaseWithId(PatientBase):
    """Base Pydantic schema extended with id field.

    Attributes:
        id (int): Unique identifier of the patient's data in the database.

    """

    id: int

    model_config = ConfigDict(from_attributes=True)
