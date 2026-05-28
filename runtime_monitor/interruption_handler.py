class InterruptionHandler:
    def __init__(self):
        self.interrupted: bool = False
        self.reason: str = ""
        self.stage: str = ""

    def interrupt(self, reason: str = "", stage: str = ""):
        self.interrupted = True
        self.reason = reason
        self.stage = stage

    def clear(self):
        self.interrupted = False
        self.reason = ""
        self.stage = ""

    def is_interrupted(self) -> bool:
        return self.interrupted

    def get_reason(self) -> str:
        return self.reason
