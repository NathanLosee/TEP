import json
import logging


def get_app_log(record):
    """Get a log record for the application.

    Args:
        record: The log record.

    Returns:
        A log record for the application.

    """
    return {
        "type": "app",
        "level": record.levelname,
        "timestamp": record.asctime,
        "message": record.getMessage(),
        "pathname": record.pathname,
        "line": record.lineno,
        "threadId": record.thread,
    }


def get_access_log(record):
    """Get a log record for access.

    Args:
        record: The log record.

    Returns:
        A log record for access.

    """
    return {
        "log": {
            "type": "access",
            "level": record.levelname,
            "timestamp": record.asctime,
            "message": record.message,
        },
        "request": record.extra_info["request"],
        "response": record.extra_info["response"],
    }


class CustomFormatter(logging.Formatter):
    """Custom formatter for logging.

    Args:
        formatter: The formatter to use.

    Returns:
        A custom formatter for logging.

    """

    def __init__(self, formatter):
        logging.Formatter.__init__(self, formatter)

    def format(self, record):
        """Format the log record.

        Args:
            record: The log record.

        Returns:
            The formatted log record.

        """
        logging.Formatter.format(self, record)
        if not hasattr(record, "extra_info"):
            return json.dumps(get_app_log(record), indent=2)
        else:
            return json.dumps(get_access_log(record), indent=2)
