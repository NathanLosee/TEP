"""Constants for system settings module."""

BASE_URL = "/system-settings"
IDENTIFIER = "SYSTEM_SETTINGS"

# Exception messages
EXC_MSG_SETTINGS_NOT_FOUND = "System settings not found."
EXC_MSG_INVALID_COLOR = "Invalid color format. Expected hex color (e.g., #FF5733)."
EXC_MSG_LOGO_TOO_LARGE = "Logo file is too large. Maximum size is 2MB."
EXC_MSG_INVALID_LOGO_TYPE = "Invalid logo file type. Allowed types: PNG, JPG, SVG."

# File constraints
MAX_LOGO_SIZE = 2 * 1024 * 1024  # 2MB
ALLOWED_LOGO_TYPES = ["image/png", "image/jpeg", "image/svg+xml"]
