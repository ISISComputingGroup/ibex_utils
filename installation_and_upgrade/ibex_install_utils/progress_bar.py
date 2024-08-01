import sys


class ProgressBar:
    """
    A simple progress bar that can be used to print/update progress in the terminal.

    To use first set the total value. To show progress bar call print()
    and to change progress modify the value of progress accordingly.
    Progress value should be <= total value.

    """
    def __init__(self):
        self.total = 0
        self.width = 20
        self.progress = 0
    
    def reset(self, total=None):
        if total is not None:
            self.total = total
        self.progress = 0

    def print(self):
        """Print/Update progress line on standard output"""
        if self.total !=0:
            percent = (self.progress / self.total) 
            arrow = '=' * int(round(self.width * percent))
            spaces = ' ' * (self.width - len(arrow))
            sys.stdout.write(f'\rProgress: [{arrow + spaces}] {int(percent * 100)}% ({self.progress} / {self.total})')
            if self.progress == self.total:
                sys.stdout.write('\n')
            sys.stdout.flush()