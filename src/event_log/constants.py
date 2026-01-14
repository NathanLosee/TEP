"""Module for defining event log-level constants."""

from src.auth_role.constants import IDENTIFIER as AUTH_ROLE_IDENTIFIER
from src.auth_role.constants import (
    MEMBERSHIP_IDENTIFIER as AUTH_ROLE_MEMBERSHIP_IDENTIFIER,
)
from src.department.constants import IDENTIFIER as DEPARTMENT_IDENTIFIER
from src.department.constants import (
    MEMBERSHIP_IDENTIFIER as DEPARTMENT_MEMBERSHIP_IDENTIFIER,
)
from src.employee.constants import IDENTIFIER as EMPLOYEE_IDENTIFIER
from src.holiday_group.constants import IDENTIFIER as HOLIDAY_GROUP_IDENTIFIER
from src.license.constants import IDENTIFIER as LICENSE_IDENTIFIER
from src.org_unit.constants import IDENTIFIER as ORG_UNIT_IDENTIFIER
from src.registered_browser.constants import (
    IDENTIFIER as REGISTERED_BROWSER_IDENTIFIER,
)
from src.timeclock.constants import IDENTIFIER as TIMECLOCK_IDENTIFIER
from src.user.constants import IDENTIFIER as USER_IDENTIFIER

IDENTIFIER = "event_log"
BASE_URL = f"/{IDENTIFIER}"
EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND = "Event log not found"
EVENT_LOG_MSGS = {
    AUTH_ROLE_IDENTIFIER: {
        "CREATE": "Auth role {auth_role_name} created",
        "UPDATE": "Auth role {auth_role_name} updated",
        "DELETE": "Auth role {auth_role_name} deleted",
    },
    AUTH_ROLE_MEMBERSHIP_IDENTIFIER: {
        "CREATE": "Auth role {auth_role_name} added to user {user_id}",
        "DELETE": "Auth role {auth_role_name} removed from user {user_id}",
    },
    DEPARTMENT_IDENTIFIER: {
        "CREATE": "Department {department_name} created",
        "UPDATE": "Department {department_name} updated",
        "DELETE": "Department {department_name} deleted",
    },
    DEPARTMENT_MEMBERSHIP_IDENTIFIER: {
        "CREATE": (
            "Employee {badge_number} added to department {department_name}"
        ),
        "DELETE": (
            "Employee {badge_number} removed from department {department_name}"
        ),
    },
    EMPLOYEE_IDENTIFIER: {
        "CREATE": "Employee {badge_number} created",
        "UPDATE": "Employee {badge_number} updated",
        "UPDATE_BADGE": (
            "Employee {badge_number} updated to {new_badge_number}"
        ),
        "DELETE": "Employee {badge_number} deleted",
    },
    HOLIDAY_GROUP_IDENTIFIER: {
        "CREATE": "Holiday {holiday_group_name} created",
        "UPDATE": "Holiday {holiday_group_name} updated",
        "DELETE": "Holiday {holiday_group_name} deleted",
    },
    LICENSE_IDENTIFIER: {
        "ACTIVATE": "License {license_key} activated",
        "DEACTIVATE": "License {license_key} deactivated",
    },
    ORG_UNIT_IDENTIFIER: {
        "CREATE": "Org unit {org_unit_name} created",
        "UPDATE": "Org unit {org_unit_name} updated",
        "DELETE": "Org unit {org_unit_name} deleted",
    },
    REGISTERED_BROWSER_IDENTIFIER: {
        "CREATE": "Registered browser {browser_uuid} created",
        "RECOVER": "Registered browser {browser_uuid} recovered",
        "DELETE": "Registered browser {browser_uuid} deleted",
    },
    TIMECLOCK_IDENTIFIER: {
        "CLOCK_IN": "Employee {badge_number} clocked in",
        "CLOCK_OUT": "Employee {badge_number} clocked out",
        "UPDATE": "Timeclock entry {timeclock_entry_id} updated",
        "DELETE": "Timeclock entry {timeclock_entry_id} deleted",
    },
    USER_IDENTIFIER: {
        "LOGIN": "User {badge_number} logged in",
        "CREATE": "User account for {badge_number} created",
        "UPDATE": "User account for {badge_number} updated",
        "UPDATE_PASSWORD": "Password updated for {badge_number} by {changed_by}",
        "DELETE": "User account for {badge_number} deleted",
    },
}
