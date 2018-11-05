"""
Classes to interact with the user
"""
from .exceptions import UserStop
import six.moves


class UserPrompt(object):
    """
    A user prompt object to ask the user questions.
    """

    # Sentinel value for allowing any answer to a prompt
    ANY = object()

    def __init__(self, automatic, confirm_steps):
        """
        Initializer.
        Args:
            automatic (bool): should the prompt ignore the user and use default responses
            confirm_steps (bool): should the user confirm a step before running it; setting automatic overrides this
        """
        self._automatic = automatic
        self._confirm_steps = confirm_steps

    def prompt(self, prompt_text, possibles, default, case_sensitive=False):
        """
        Prompt the user for an answer and check that answer. If in auto mode just answer the default
        Args:
            prompt_text: Text to prompt
            possibles: allowed answers
            default: default answer if in automatic mode, if None still ask the user even in automatic mode
            case_sensitive: is the answer case sensitive

        Returns: answer from possibles

        """
        if self._automatic and default is not None:
            print("{prompt} : {default}".format(prompt=prompt_text, default=default))
            return default
        elif possibles is UserPrompt.ANY:
            return six.moves.input(prompt_text).strip()
        else:
            return self._get_user_answer(prompt_text, possibles, case_sensitive)

    def _get_user_answer(self, prompt_text, possibles, case_sensitive=False):
        while True:
            answer = six.moves.input(prompt_text).strip()
            for possible in possibles:
                if answer == possible or (not case_sensitive and possible.lower() == answer.lower()):
                    return possible
            print("Answer is not allowed can be one of ({0})".format(possibles))

    def confirm_step(self, step_text):
        """
        Confirm that a step should be done if in confirm steps mode
        Args:
            step_text: the text for the step

        Returns: true if step should continue; False otherwise

        """
        if not self._confirm_steps or self._automatic:
            return True
        return self._get_user_answer("Do step '{0}'? : ".format(step_text), ("Y", "N")) == "Y"

    def prompt_and_raise_if_not_yes(self, message, default="N"):
        """
        Prompt the user and raise and exception if they do not answer yes
        Default to Y in quiet mode
        Args:
            message: the message to prompt the user with
            default: default answer if in automatic mode
        Raises UserStop: if the user does not answer Y
        """
        if self.prompt("{}\nType Y when done.".format(message), possibles=["Y", "N"], default=default) != "Y":
            raise UserStop
