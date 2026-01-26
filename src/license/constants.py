"""Module for defining license constants.

Constants:
    - IDENTIFIER: The table name for licenses.
    - BASE_URL: The base URL for license endpoints.

"""

import os

IDENTIFIER = "licenses"
BASE_URL = f"/{IDENTIFIER}"
EXC_MSG_LICENSE_NOT_FOUND = "License not found"
EXC_MSG_INVALID_LICENSE_KEY = "Invalid license key format"
EXC_MSG_LICENSE_SERVER_ERROR = "Unable to contact license server"
EXC_MSG_LICENSE_ACTIVATION_FAILED = "License activation failed"
EXC_MSG_LICENSE_REQUIRED = "This operation requires an active license"

# License server URL - configure via environment variable
LICENSE_SERVER_URL = os.getenv("LICENSE_SERVER_URL", "http://localhost:8001")
