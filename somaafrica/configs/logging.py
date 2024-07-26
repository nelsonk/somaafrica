import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler

from .settings import access_log_file, error_log_file


class Logger:
    """
    Logger configuration
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):  # Avoid re-initializing
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.DEBUG)

            self.error_file_handler = RotatingFileHandler(
                error_log_file, maxBytes=500 * 1024 * 1024, backupCount=3
            )
            self.error_file_handler.setLevel(logging.ERROR)
            self.access_file_handler = TimedRotatingFileHandler(
                access_log_file, when="midnight", interval=2, backupCount=3
            )
            self.access_file_handler.setLevel(logging.DEBUG)
            self.console_handler = logging.StreamHandler()
            self.console_handler.setLevel(logging.INFO)

            self.error_file_handler.setFormatter(self.format_log())
            self.access_file_handler.setFormatter(self.format_log())
            self.console_handler.setFormatter(self.format_log())

            self.logger.addHandler(self.error_file_handler)
            self.logger.addHandler(self.access_file_handler)
            self.logger.addHandler(self.console_handler)

            self.initialized = True

    def format_log(self):
        """
        Format logs like this
        """
        return logging.Formatter(
            "[%(asctime)s] %(levelname)s {%(pathname)s:%(lineno)d} - %(message)s"  # noqa
        )


def get_logger():
    """
    Return logger
    """
    return Logger().logger
