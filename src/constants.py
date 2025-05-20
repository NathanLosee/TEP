"""Module for defining global-level constants."""

DIGIT_REGEX = "[[:digit:]]"
CAP_CHAR_REGEX = "[[:upper:]]"
NAME_CHAR_REGEX = "[-'' [:alpha:]]"
EXC_MSG_IDS_DO_NOT_MATCH = "Ids in body and path do not match."

RESOURCE_SCOPES = {
    "auth_role.create": "Create Auth Role",
    "auth_role.read": "Read Auth Role",
    "auth_role.update": "Update Auth Role",
    "auth_role.delete": "Delete Auth Role",
    "auth_role.assign": "Assign Auth Role",
    "auth_role.unassign": "Unassign Auth Role",
    "department.create": "Create Department",
    "department.read": "Read Department",
    "department.update": "Update Department",
    "department.delete": "Delete Department",
    "department.assign": "Assign Department",
    "department.unassign": "Unassign Department",
    "employee.create": "Create Employee",
    "employee.read": "Read Employee",
    "employee.update": "Update Employee",
    "employee.update.badge_number": "Update Employee's Badge Number",
    "employee.delete": "Delete Employee",
    "event_log.create": "Create Event Log",
    "event_log.read": "Read Event Log",
    "event_log.delete": "Delete Event Log",
    "holiday_group.create": "Create Holiday Group",
    "holiday_group.read": "Read Holiday Group",
    "holiday_group.update": "Update Holiday Group",
    "holiday_group.delete": "Delete Holiday Group",
    "org_unit.create": "Create Org Unit",
    "org_unit.read": "Read Org Unit",
    "org_unit.update": "Update Org Unit",
    "org_unit.delete": "Delete Org Unit",
    "timeclock.update": "Update Timeclock entry",
    "timeclock.read": "Read Timeclock entry",
    "timeclock.delete": "Delete Timeclock entry",
    "user.create": "Create User",
    "user.read": "Read User",
    "user.update": "Update User",
    "user.delete": "Delete User",
}
