"""Module for defining patient-level constants."""

from src.constants import DIGIT_REGEX as D, NAME_REGEX as N

BASE_URL = "/patients"
NAME_REGEX = f"^{N}+$"
SSN_REGEX = f"^{D}{{3}}-{D}{{2}}-{D}{{4}}$"
EMAIL_REGEX = "[^@]+@[^@]+[.][^@]+"
POSTAL_REGEX = f"^({D}{{5}}|{D}{{5}}-{D}{{4}})$"
PERMITTED_GENDER_INPUTS = ["male", "female", "other"]
PERMITTED_GENDER_INPUTS_STR = (
    str(PERMITTED_GENDER_INPUTS).replace("[", "(").replace("]", ")")
)
PERMITTED_STATE_ABBREVIATIONS = [
    "al",
    "ak",
    "az",
    "ar",
    "ca",
    "co",
    "ct",
    "de",
    "fl",
    "ga",
    "hi",
    "ia",
    "id",
    "il",
    "in",
    "ks",
    "ky",
    "la",
    "ma",
    "me",
    "md",
    "mi",
    "mn",
    "mo",
    "ms",
    "mt",
    "nc",
    "nd",
    "ne",
    "nh",
    "nj",
    "nm",
    "nv",
    "ny",
    "oh",
    "ok",
    "or",
    "pa",
    "ri",
    "sc",
    "sd",
    "tn",
    "tx",
    "ut",
    "va",
    "vt",
    "wa",
    "wv",
    "wi",
    "wy",
]
PERMITTED_STATE_ABBREVIATIONS_STR = (
    str(PERMITTED_STATE_ABBREVIATIONS).replace("[", "(").replace("]", ")")
)
EXCEPTION_MESSAGE_STATE_NOT_VALID = (
    "State must be a valid US state abbreviation."
)
EXCEPTION_MESSAGE_GENDER_INPUT_NOT_VALID = (
    f"Gender must be one of {PERMITTED_GENDER_INPUTS}."
)
EXCEPTION_MESSAGE_EMAIL_NOT_UNIQUE = "Patient email already in use."
EXCEPTION_MESSAGE_PATIENT_NOT_FOUND = "Patient does not exist."
EXCEPTION_MESSAGE_PATIENT_HAS_ENCOUNTERS = "Patient has encounters."
