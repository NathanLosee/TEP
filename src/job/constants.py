"""Module for defining job-level constants."""

from src.constants import NAME_CHAR_REGEX as N

IDENTIFIER = "jobs"
BASE_URL = f"/{IDENTIFIER}"
NAME_REGEX = f"^{N}+$"
NAME_MAX_LENGTH = 100
EXC_MSG_NAME_ALREADY_EXISTS = (
    "Job with name already exists within this department."
)
EXC_MSG_JOB_NOT_FOUND = "Job does not exist."
EXC_MSG_EMPLOYEES_ASSIGNED = "Employees are assigned to this job."
