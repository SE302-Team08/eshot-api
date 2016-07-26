import time

class Timer(object):
    def __init__(self):
        self.start = None
        self.finish = None

    def begin(self):
        self.start = time.time()

    def end(self):
        self.finish = time.time()

    def __call__(self, *args, **kwargs):
        return self.finish - self.start

    def __str__(self):
        return str(self.finish - self.start)