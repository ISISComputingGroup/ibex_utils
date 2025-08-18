import os
import sys
import time
from contextlib import contextmanager
from typing import Generator

ENABLE_LOGGING = True


@contextmanager
def temporarily_disable_logging() -> Generator[None, None, None]:
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

    def __init__(self) -> None:
        current_date = time.strftime("%Y%m%d")
        log_file = f"DEPLOY-{current_date}.log"
        log_directory = os.path.join("C:\\", "Instrument", "var", "logs", "deploy")
        os.makedirs(log_directory, exist_ok=True)
        log_path = os.path.join(log_directory, log_file)

        self.console = sys.stdout
        self.input = sys.stdin
        self.log = open(log_path, "a")
        print(f"Log file is {log_path}")

    def write(self, message: str) -> int:
        if ENABLE_LOGGING:
            self.log.write(message)
        else:
            self.log.write("[concealed]\n")
        return self.console.write(message)

    def flush(self) -> None:
        self.console.flush()
        self.log.flush()

    def readline(self) -> str:
        text = self.input.readline()
        if ENABLE_LOGGING:
            self.log.write(text)
        else:
            self.log.write("[concealed]\n")
        return text

    @staticmethod
    def set_up() -> None:
        logger = Logger()
        sys.stdout = logger
        sys.stderr = logger
        sys.stdin = logger
