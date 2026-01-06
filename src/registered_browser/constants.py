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
EXC_MSG_BROWSER_UUID_REQUIRED = "Browser UUID is required"
