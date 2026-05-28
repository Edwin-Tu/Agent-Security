from abc import ABC, abstractmethod


class BaseSkill(ABC):
    def __init__(self, name: str = None, description: str = None):
        self.name = name or self.__class__.__name__
        self.description = description or ""

    @abstractmethod
    def detect(self, text: str, context: dict = None) -> dict:
        pass

    @abstractmethod
    def defend(self, text: str, threat_info: dict) -> str:
        pass

    def process(self, text: str, context: dict = None) -> dict:
        threat_info = self.detect(text, context)
        if threat_info.get("detected", False):
            sanitized = self.defend(text, threat_info)
            return {"intervened": True, "original": text, "sanitized": sanitized, "threat": threat_info}
        return {"intervened": False, "original": text, "sanitized": text, "threat": threat_info}
