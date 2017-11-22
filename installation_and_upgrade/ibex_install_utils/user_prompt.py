"""
Classes to interact with the user
"""
from exceptions import UserStop


class UserPrompt(object):
    """
    A user prompt object to ask the user questions.
    """
    def __init__(self, automatic, confirm_steps):
        """
        Initializer.
        Args:
            automatic: should the prompt ignore the user and use default responses
            confirm_steps: should the user confirm a step before running it; setting automatic overides this
        """
        self._automatic = automatic
        self._confirm_steps = confirm_steps

    def prompt(self, prompt_text, possibles, default, case_sensitive=False):
        """
        Prompt the user for an answer and check that answer. If in auto mode just answer the default
        Args:
            prompt_text: Text to prompt
            possibles: allowed answers
            default: default answer if in automatic mode
            case_sensitive: is the answer case sensitive

        Returns: answer from possibles

        """
        if self._automatic:
            print("{prompt} : {default}".format(prompt=prompt_text, default=default))
            return default

        return self._get_user_answer(prompt_text, possibles, case_sensitive)

    def _get_user_answer(self, prompt_text, possibles, case_sensitive=False):
        while True:
            answer = raw_input(prompt_text).strip()
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

    def prompt_and_raise_if_not_yes(self, string):
        if self.prompt("{}\nType Y when done.".format(string), ["Y", "N"], "N") != "Y":
            raise UserStop
