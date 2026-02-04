"""Module for defining registered browser constants.

Constants:
    - IDENTIFIER: The table name for registered browsers.
    - BASE_URL: The base URL for registered browser endpoints.
    - RESOURCE_NAME: The resource name for permissions.

"""

IDENTIFIER = "registered_browsers"
BASE_URL = f"/{IDENTIFIER}"
RESOURCE_NAME = "registered_browser"
EXC_MSG_BROWSER_NOT_FOUND = "Registered browser not found"
EXC_MSG_BROWSER_ALREADY_REGISTERED = "Browser already registered"
EXC_MSG_BROWSER_NAME_ALREADY_EXISTS = (
    "Browser name already exists. "
    "Please choose a different name."
)
EXC_MSG_BROWSER_UUID_REQUIRED = "Browser UUID is required"
EXC_MSG_INVALID_UUID_FORMAT = (
    "Invalid UUID format. "
    "Expected format: WORD-WORD-WORD-NUMBER"
)
EXC_MSG_INVALID_DEVICE_ID_FORMAT = (
    "Invalid device ID format. "
    "Expected format: WORD-WORD-WORD-NUMBER"
)
EXC_MSG_DEVICE_NOT_FOUND = (
    "Device ID not found or browser is inactive"
)
EXC_MSG_SESSION_CONFLICT = (
    "This device ID is currently in use by another browser."
    " Please wait a few minutes and try again,"
    " or contact an administrator."
)
