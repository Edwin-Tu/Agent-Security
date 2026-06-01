class ConfidenceScorer:
    @staticmethod
    def compute_category_score(
        base_confidence: float,
        matched_weights: list[float],
    ) -> float:
        total = base_confidence + sum(matched_weights)
        return min(total, 1.0)

    @staticmethod
    def compute_severity_hint(
        matched_rules: list[dict],
        primary_category: str = None,
        attack_map: dict[str, dict] = None,
    ) -> str:
        if primary_category and attack_map:
            attack_def = attack_map.get(primary_category, {})
            return attack_def.get("severity_hint", "low")

        severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        max_sev = "low"
        for rule in matched_rules:
            sev = rule.get("severity_hint", "low")
            if severity_order.get(sev, 0) > severity_order.get(max_sev, 0):
                max_sev = sev
        return max_sev

    @staticmethod
    def has_phrase_or_regex(rule: dict) -> bool:
        return bool(rule.get("phrases") or rule.get("regex"))

    @staticmethod
    def pick_primary_category(
        category_scores: dict[str, float],
        category_matches: dict[str, list[dict]] = None,
    ) -> str:
        if not category_scores:
            return "benign"

        max_score = max(category_scores.values())
        top_categories = [c for c, s in category_scores.items() if s == max_score]

        if len(top_categories) == 1:
            return top_categories[0]

        if category_matches:
            for cat in top_categories:
                rules = category_matches.get(cat, [])
                if any(ConfidenceScorer.has_phrase_or_regex(r) for r in rules):
                    return cat

        return top_categories[0]
