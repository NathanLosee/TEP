"""Module for defining updater constants.

Constants:
    - IDENTIFIER: The identifier for updater event logs.
    - BASE_URL: The base URL for updater endpoints.

"""

IDENTIFIER = "updater"
BASE_URL = f"/{IDENTIFIER}"
EXC_MSG_NOT_CONFIGURED = "GITHUB_REPO is not configured"
EXC_MSG_NO_UPDATE_AVAILABLE = "No update available"
EXC_MSG_DOWNLOAD_IN_PROGRESS = "A download is already in progress"
EXC_MSG_NO_DOWNLOAD_READY = "No downloaded update ready to apply"
EXC_MSG_NOT_FROZEN = (
    "Updates can only be applied to packaged deployments"
)
EXC_MSG_NO_BACKUP = "No backup available for rollback"
