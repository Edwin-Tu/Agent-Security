class InterruptionHandler:
    def __init__(self):
        self.interrupted: bool = False
        self.reason: str = ""

    def interrupt(self, reason: str = ""):
        self.interrupted = True
        self.reason = reason

    def clear(self):
        self.interrupted = False
        self.reason = ""

    def is_interrupted(self) -> bool:
        return self.interrupted

    def get_reason(self) -> str:
        return self.reason
