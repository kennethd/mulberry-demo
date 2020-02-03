
import logging


class NullHandler(logging.Handler):
    """Null log handler can be registered with app to suppress "no handlers" error

    https://docs.python.org/2.6/library/logging.html#configuring-logging-for-a-library
    """

    def emit(self, record):
        pass
