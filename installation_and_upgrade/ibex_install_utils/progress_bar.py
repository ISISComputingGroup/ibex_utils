import sys

class ProgressBar:

    def __init__(self):
      self.total = 0
      self.width = 20
      self.progress = 0
    
    def print(self):
       if self.total !=0:
            percent = (self.progress / self.total) 
            arrow = '=' * int(round(self.width * percent))
            spaces = ' ' * (self.width - len(arrow))
            sys.stdout.write(f'\rProgress: [{arrow + spaces}] {int(percent * 100)}% ({self.progress} / {self.total})')
            if self.progress == self.total:
                sys.stdout.write('\n')
            sys.stdout.flush()