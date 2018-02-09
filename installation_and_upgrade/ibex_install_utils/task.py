"""
Task infrastructure.
"""


class Task(object):
    """
    Task to be performed for install.

    Confirms a step is to be run (if needed) and places the answer in do_step.
    Wraps the task in print statements so users can see when a task starts and ends.
    """

    def __init__(self, task_name, user_prompt):
        """
        Initialised.
        Args:
            task_name: the name of the task
            user_prompt: object allowing the user to be prompted for an answer
        """
        self._task = task_name
        self._user_prompt = user_prompt
        self.do_step = True

    def __enter__(self):
        self.do_step = self._user_prompt.confirm_step(self._task)
        print("{task} ...".format(task=self._task))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            print("... Done".format(task=self._task))
