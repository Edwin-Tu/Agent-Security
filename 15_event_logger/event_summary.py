from collections import Counter


class EventSummary:
    def __init__(self, events: list[dict]):
        self.events = events

    def build(self) -> dict:
        total = len(self.events)
        if total == 0:
            return {
                "total_events": 0,
                "allow_count": 0,
                "warn_count": 0,
                "rewrite_count": 0,
                "restrict_count": 0,
                "block_count": 0,
                "authorize_count": 0,
                "escalate_count": 0,
                "leakage_count": 0,
                "blocked_count": 0,
                "highest_risk_score": 0,
                "average_risk_score": 0.0,
                "most_common_attack_type": "",
                "most_common_policy_action": "",
                "most_common_enabled_skill": "",
            }

        action_counts = Counter(e.get("policy_action", "ALLOW") for e in self.events)
        attack_counts = Counter(e.get("attack_type", "unknown") for e in self.events)
        blocked_count = sum(1 for e in self.events if e.get("blocked", False))
        leakage_count = sum(1 for e in self.events if e.get("leakage_detected", False))
        risk_scores = [e.get("risk_score", 0) for e in self.events]

        all_skills = []
        for e in self.events:
            skills = e.get("enabled_skills", [])
            all_skills.extend(skills)
        skill_counter = Counter(all_skills)

        return {
            "total_events": total,
            "allow_count": action_counts.get("ALLOW", 0),
            "warn_count": action_counts.get("WARN", 0),
            "rewrite_count": action_counts.get("REWRITE", 0),
            "restrict_count": action_counts.get("RESTRICT", 0),
            "block_count": action_counts.get("BLOCK", 0),
            "authorize_count": action_counts.get("AUTHORIZE", 0),
            "escalate_count": action_counts.get("ESCALATE", 0),
            "leakage_count": leakage_count,
            "blocked_count": blocked_count,
            "highest_risk_score": max(risk_scores),
            "average_risk_score": round(sum(risk_scores) / total, 1),
            "most_common_attack_type": attack_counts.most_common(1)[0][0] if attack_counts else "",
            "most_common_policy_action": action_counts.most_common(1)[0][0] if action_counts else "",
            "most_common_enabled_skill": skill_counter.most_common(1)[0][0] if skill_counter else "",
        }
