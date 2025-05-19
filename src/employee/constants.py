"""Module for defining employee-level constants."""

from src.constants import NAME_CHAR_REGEX as N

IDENTIFIER = "employees"
BASE_URL = f"/{IDENTIFIER}"
NAME_REGEX = f"^{N}+$"
EXC_MSG_EMPLOYEE_NOT_FOUND = "Employee does not exist."
EXC_MSG_EMPLOYEE_WITH_SAME_ID_EXISTS = "Employee with same ID already exists."
