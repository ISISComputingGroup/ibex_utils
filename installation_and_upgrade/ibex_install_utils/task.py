"""
Task infrastructure.
"""
import traceback

from installation_and_upgrade.ibex_install_utils.exceptions import UserStop, ErrorInTask
from installation_and_upgrade.ibex_install_utils.user_prompt import UserPrompt


def _run_task_to_completion(task_name, prompt, self_decorated_method, func, args, kwargs):
    try:
        func(self_decorated_method, *args, **kwargs)
        print("... Done")
        return True
    except UserStop as ex:
        raise ex
    except Exception:
        print(f"Error in task '{task_name}'")
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
            raise ErrorInTask("Task aborted")


def task(task_name, attribute_name="prompt"):
    """
        Decorator for tasks to be performed for installs.

        Confirms a step is to be run (if needed). If there is a problem will ask the user what to do.
        Wraps the task in print statements so users can see when a task starts and ends.
        """

    def _task_with_name_decorator(func):
        def _wrapper(self_of_decorated_method, *args, **kwargs):
            prompt = getattr(self_of_decorated_method, attribute_name)
            if prompt.confirm_step(task_name):
                print(f"{task_name} ...")
                while True:
                    if _run_task_to_completion(task_name, prompt, self_of_decorated_method, func, args, kwargs):
                        break
        return _wrapper
    return _task_with_name_decorator


if __name__ == "__main__":

    class TaskTest:
        """Test Task"""
        def __init__(self):
            self.prompt = UserPrompt(False, True)

        @task("play it again")
        def play(self):
            """Play"""
            print("hi")
            raise ValueError("blag")

    t = TaskTest()

    t.play()
