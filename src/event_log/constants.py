"""Module for defining event log-level constants."""

from src.auth_role.constants import (
    IDENTIFIER as AUTH_ROLE_IDENTIFIER,
    MEMBERSHIP_IDENTIFIER as AUTH_ROLE_MEMBERSHIP_IDENTIFIER,
)
from src.department.constants import (
    IDENTIFIER as DEPARTMENT_IDENTIFIER,
    MEMBERSHIP_IDENTIFIER as DEPARTMENT_MEMBERSHIP_IDENTIFIER,
)
from src.employee.constants import IDENTIFIER as EMPLOYEE_IDENTIFIER
from src.holiday_group.constants import IDENTIFIER as HOLIDAY_GROUP_IDENTIFIER
from src.org_unit.constants import IDENTIFIER as ORG_UNIT_IDENTIFIER
from src.timeclock.constants import IDENTIFIER as TIMECLOCK_IDENTIFIER


IDENTIFIER = "event_log"
LOGIN_IDENTIFIER = "login"
BASE_URL = f"/{IDENTIFIER}"
EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND = "Event log not found"
EVENT_LOG_MSGS = {
    AUTH_ROLE_IDENTIFIER: {
        "CREATE": "Auth role {auth_role_id} created",
        "UPDATE": "Auth role {auth_role_id} updated",
        "DELETE": "Auth role {auth_role_id} deleted",
    },
    AUTH_ROLE_MEMBERSHIP_IDENTIFIER: {
        "CREATE": ("Auth role {auth_role_id} added to employee {employee_id}"),
        "DELETE": (
            "Auth role {auth_role_id} removed from employee {employee_id}"
        ),
    },
    DEPARTMENT_IDENTIFIER: {
        "CREATE": "Department {department_id} created",
        "UPDATE": "Department {department_id} updated",
        "DELETE": "Department {department_id} deleted",
    },
    DEPARTMENT_MEMBERSHIP_IDENTIFIER: {
        "CREATE": (
            "Department {department_id} assigned to employee {employee_id}"
        ),
        "DELETE": (
            "Department {department_id} unassigned from employee {employee_id}"
        ),
    },
    EMPLOYEE_IDENTIFIER: {
        "CREATE": "Employee {employee_id} created",
        "UPDATE": "Employee {employee_id} updated",
        "DELETE": "Employee {employee_id} deleted",
    },
    HOLIDAY_GROUP_IDENTIFIER: {
        "CREATE": "Holiday {holiday_group_id} created",
        "UPDATE": "Holiday {holiday_group_id} updated",
        "DELETE": "Holiday {holiday_group_id} deleted",
    },
    LOGIN_IDENTIFIER: {
        "LOGIN": "Employee {employee_id} logged in",
    },
    ORG_UNIT_IDENTIFIER: {
        "CREATE": "Org unit {org_unit_id} created",
        "UPDATE": "Org unit {org_unit_id} updated",
        "DELETE": "Org unit {org_unit_id} deleted",
    },
    TIMECLOCK_IDENTIFIER: {
        "CLOCK_OUT": "Employee {employee_id} clocked in",
        "CLOCK_IN": "Employee {employee_id} clocked out",
        "UPDATE": "Timeclock entry {timeclock_entry_id} updated",
        "DELETE": "Timeclock entry {timeclock_entry_id} deleted",
    },
}
