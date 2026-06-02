class InterruptionHandler:
    def __init__(self):
        self.interrupted = False
        self.reason = ""

    def interrupt(self, reason: str = ""):
        self.interrupted = True
        self.reason = reason

    def clear(self):
        self.interrupted = False
        self.reason = ""
