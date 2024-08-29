import errno
import os
from logging.handlers import TimedRotatingFileHandler


def mkdir_p(path):
    """Create a directory if it does not exist.

    Args:
        path: The path to the directory.

    Raises:
        OSError: If the directory cannot be created.

    """
    try:
        os.makedirs(path, exist_ok=True)
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    """Custom timed rotating file handler.

    Args:
        filename: The name of the log file.
        when: The type of interval.
        interval: The interval.
        backupCount: The number of backups to keep.
        encoding: The encoding.
        delay: Whether to delay.
        utc: Whether to use UTC.
        atTime: The time.
        errors: The error handling scheme.

    """

    def __init__(
        self,
        filename,
        when="h",
        interval=1,
        backupCount=0,
        encoding=None,
        delay=False,
        utc=False,
        atTime=None,
        errors=None,
    ):
        mkdir_p(os.path.dirname(filename))
        TimedRotatingFileHandler.__init__(
            self,
            filename,
            when,
            interval,
            backupCount,
            encoding,
            delay,
            utc,
            atTime,
            errors,
        )
