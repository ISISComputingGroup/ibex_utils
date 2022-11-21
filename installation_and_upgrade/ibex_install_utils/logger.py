import os
import sys
import time


class Logger:
    """
    Logger class used to capture output and input to a log file.
    """
    def __init__(self):
        CURRENT_DATE = time.strftime("%Y%m%d")
        LOG_FILE = f"DEPLOY-{CURRENT_DATE}.log"
        LOG_DIRECTORY = os.path.join("C:\\", "Instrument", "var", "logs", "deploy")
        if not os.path.exists(LOG_DIRECTORY):
            os.mkdir(LOG_DIRECTORY)
        LOG_PATH = os.path.join(LOG_DIRECTORY, LOG_FILE)

        self.console = sys.stdout
        self.input = sys.stdin
        self.log = open(LOG_PATH, "a")
        print(f"Log file is {LOG_PATH}")
        
    def write(self, message):
        self.log.write(message)
        return self.console.write(message)
        
    def flush(self):
        self.console.flush()
        self.log.flush()

    def readline(self):
        text = self.input.readline()
        self.log.write(text)
        return text
        
    @staticmethod
    def set_up():
        logger = Logger()
        sys.stdout = logger
        sys.stderr = logger
        sys.stdin = logger
