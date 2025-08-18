import os
import sys
import time
from contextlib import contextmanager

ENABLE_LOGGING = True


@contextmanager
def temporarily_disable_logging():
    global ENABLE_LOGGING
    previous_logging_enabled = ENABLE_LOGGING
    ENABLE_LOGGING = False
    try:
        yield
    finally:
        ENABLE_LOGGING = previous_logging_enabled


class Logger:
    """
    Logger class used to capture output and input to a log file.
    """

    def __init__(self):
        CURRENT_DATE = time.strftime("%Y%m%d")
        LOG_FILE = f"DEPLOY-{CURRENT_DATE}.log"
        LOG_DIRECTORY = os.path.join("C:\\", "Instrument", "var", "logs", "deploy")
        os.makedirs(LOG_DIRECTORY, exist_ok=True)
        LOG_PATH = os.path.join(LOG_DIRECTORY, LOG_FILE)

        self.console = sys.stdout
        self.input = sys.stdin
        self.log = open(LOG_PATH, "a")
        print(f"Log file is {LOG_PATH}")

    def write(self, message):
        if ENABLE_LOGGING:
            self.log.write(message)
        else:
            self.log.write("[concealed]\n")
        return self.console.write(message)

    def flush(self):
        self.console.flush()
        self.log.flush()

    def readline(self):
        text = self.input.readline()
        if ENABLE_LOGGING:
            self.log.write(text)
        else:
            self.log.write("[concealed]\n")
        return text

    @staticmethod
    def set_up():
        logger = Logger()
        sys.stdout = logger
        sys.stderr = logger
        sys.stdin = logger
