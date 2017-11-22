"""
Exceptions thrown by the upgrade utilities
"""


class UserStop(Exception):
    """
    Exception when a task stops because of a user request
    """
    pass


class ErrorInTask(Exception):
    """
    Exception if there is an error when running a task.
    """

    def __init__(self, message):
        self.message = message


class ErrorInRun(ErrorInTask):
    """
    Exception if there is an error when running a process.
    """
    def __init__(self, message):
        super(ErrorInRun, self).__init__(message)


class ErrorWithFile(ErrorInTask):
    """
    Exception if there is an error when doing something with a file
    """
    def __init__(self, message):
        super(ErrorWithFile, self).__init__(message)