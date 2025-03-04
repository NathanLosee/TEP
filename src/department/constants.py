"""Module for defining department-level constants."""

from src.constants import NAME_CHAR_REGEX as N

IDENTIFIER = "departments"
MEMBERSHIP_IDENTIFIER = "department_memberships"
BASE_URL = f"/{IDENTIFIER}"
NAME_REGEX = f"^{N}+$"
NAME_MAX_LENGTH = 100
EXC_MSG_NAME_ALREADY_EXISTS = "Department with name already exists."
EXC_MSG_DEPARTMENT_NOT_FOUND = "Department does not exist."
EXC_MSG_EMPLOYEE_IS_MEMBER = "The employee is already in this department."
EXC_MSG_EMPLOYEE_NOT_MEMBER = "The employee is not in this department."
EXC_MSG_EMPLOYEES_ASSIGNED = "Employees are assigned to this department."
EXC_MSG_JOBS_ASSIGNED = "Jobs are assigned to this department."
