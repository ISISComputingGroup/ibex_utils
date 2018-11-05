"""
Task infrastructure.
"""
import traceback

from ibex_install_utils.exceptions import UserStop
from ibex_install_utils.user_prompt import UserPrompt


def task(task_name, attribute_name="_prompt"):
    """
        Decorator for tasks to be performed for installs.

        Confirms a step is to be run (if needed). If there is a problem will ask the user what to do.
        Wraps the task in print statements so users can see when a task starts and ends.
        """

    def _task_with_name_decorator(func):
        def _wrapper(class_of_decorated_method, *args, **kwargs):
            prompt = getattr(class_of_decorated_method, attribute_name)
            if prompt.confirm_step(task_name):
                print("{} ...".format(task_name))
                while not _run_task(class_of_decorated_method, args, kwargs, prompt):
                    pass

        def _run_task(class_of_decorated_method, args, kwargs, prompt):
            try:
                func(class_of_decorated_method, *args, **kwargs)
                print("... Done")
                return True
            except UserStop as ex:
                raise ex
            except Exception:
                print("Error in task '{}'".format(task_name))
                traceback.print_exc()

                answer = prompt.prompt(
                    "Do you want to R: restart task, S: skip and continue with next task, A: abort script: ",
                    possibles=["R", "S", "A"], default="A")
                if answer == "R":
                    return False
                elif answer == "S":
                    print("... Skipping task")
                    return True
                else:
                    raise UserStop()

        return _wrapper
    return _task_with_name_decorator


if __name__ == "__main__":

    class TaskTest:
        """Test Task"""
        def __init__(self):
            self._prompt = UserPrompt(False, True)

        @task("play it again")
        def play(self):
            """Play"""
            print("hi")
            raise ValueError("blag")

    t = TaskTest()

    t.play()
