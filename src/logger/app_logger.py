import logging

from src.logger.file_handler import CustomTimedRotatingFileHandler


def get_file_handler(formatter, log_filename, log_level):
    """Get a file handler for logging.

    Args:
        formatter: The formatter to use.
        log_filename: The name of the log file.
        log_level: The log level.

    Returns:
        A file handler for logging.

    """
    file_handler = CustomTimedRotatingFileHandler(
        log_filename, when="midnight", backupCount=7, utc=True
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    return file_handler


def get_stream_handler(formatter, log_level):
    """Get a stream handler for logging.

    Args:
        formatter: The formatter to use.
        log_level: The log level.

    Returns:
        A stream handler for logging.

    """
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(log_level)
    return stream_handler


def get_logger(
    name,
    formatter,
    log_filename="logs/logfile.log",
    log_level="INFO",
):
    """Get a logger.

    Args:
        name: The name of the logger.
        formatter: The formatter to use.
        log_filename: The name of the log file.
        log_level: The log level.

    Returns:
        A logger.

    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.addHandler(get_file_handler(formatter, log_filename, log_level))
    logger.addHandler(get_stream_handler(formatter, log_level))
    logger.propagate = False
    return logger
