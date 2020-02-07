import sys

import logging

StderrHandler = logging.StreamHandler(sys.stderr)
StderrHandler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
StderrHandler.setFormatter(formatter)

class NullHandler(logging.Handler):
    """Null log handler can be registered with app to suppress "no handlers" error

    https://docs.python.org/2.6/library/logging.html#configuring-logging-for-a-library
    """

    def emit(self, record):
        pass

def getLogger(name):
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    if not log.handlers:
        log.addHandler(StderrHandler)

    return log

