from datetime import datetime


class PercentTracker():
    def __init__(self, step=1):
        self.amount = 0
        self.counter = 0
        self.start = datetime.now()
        self.step = step

    def restart_clock(self):
        self.start = datetime.now()

    def print_message(self, param=None):
        elapsed = datetime.now() - self.start
        self.counter += 1
        percentage = (float(self.counter) / float(self.amount)) * 100
        percent = round(percentage, 3)
        percent = format(percent, '.3f')
        message = f"{elapsed}\t{self.counter} of {self.amount}\t{percent}%"
        if self.counter % self.step == 0 or self.counter == self.amount:
            if param:
                message += f"\t{param}"
            return message
