"""Module for defining timeclock-level constants."""

IDENTIFIER = "timeclock"
BASE_URL = f"/{IDENTIFIER}"
EXC_MSG_CLOCK_OUT_BEFORE_CLOCK_IN = (
    "clock_out must be greater than or equal to clock_in."
)
EXC_MSG_TIMECLOCK_ENTRY_NOT_FOUND = "Timeclock entry not found"
EXC_MSG_EMPLOYEE_NOT_ALLOWED = "Employee is not allowed to clock in/out"
