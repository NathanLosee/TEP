"""Module for defining license constants.

Constants:
    - IDENTIFIER: The table name for licenses.
    - BASE_URL: The base URL for license endpoints.

"""

IDENTIFIER = "licenses"
BASE_URL = f"/{IDENTIFIER}"
EXC_MSG_LICENSE_NOT_FOUND = "License not found"
EXC_MSG_INVALID_LICENSE_KEY = "Invalid license key or signature"
EXC_MSG_LICENSE_ALREADY_ACTIVATED = "A license is already activated"
EXC_MSG_LICENSE_REQUIRED = "This operation requires an active license"
