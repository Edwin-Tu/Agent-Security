from .attack_classifier import AttackClassifier
from .defense_context import DefenseContext
from .risk_score import RiskScore
from .session_memory import SessionMemory


class DefenseRouter:
    def __init__(self):
        self.classifier = AttackClassifier()
        self.context = DefenseContext()
        self.risk_score = RiskScore()
        self.memory = SessionMemory()
        self.skills: list = []
        self.guards: list = []

    def register_skill(self, skill):
        self.skills.append(skill)

    def register_guard(self, guard):
        self.guards.append(guard)

    def analyze(self, text: str, history: list[str] = None) -> dict:
        threats = self.classifier.classify_with_context(text, history)
        risk_result = self.risk_score.compute(threats)
        return {
            "threats": threats,
            "risk": risk_result,
            "blocked": self.risk_score.exceeds_threshold(threats, self.context.get_threshold()),
        }

    def execute_defenses(self, text: str, analysis: dict) -> str:
        if analysis["blocked"]:
            self.context.record_intervention("pre_input", "Risk threshold exceeded", analysis)
            return self._build_rejection(analysis)
        sanitized = text
        for guard in self.guards:
            result = guard.check(sanitized)
            if result.get("blocked"):
                self.context.record_intervention("guard", guard.__class__.__name__, result)
                return self._build_rejection(result)
        return sanitized

    def process(self, text: str, history: list[str] = None) -> dict:
        orig_text = text
        analysis = self.analyze(text, history)
        self.context.record_intervention("analysis", "Input analyzed", analysis)
        processed = self.execute_defenses(text, analysis)
        blocked = processed != orig_text
        interaction = {
            "input": orig_text,
            "output": processed,
            "blocked": blocked,
            "analysis": analysis,
        }
        self.memory.record(interaction)
        return interaction

    def _build_rejection(self, info: dict) -> str:
        return "[SecretGuard]\n此內容受到限制，未經授權無法提供。"

    def summary(self) -> dict:
        return {
            "stats": self.memory.stats(),
            "context": self.context.summary(),
        }
