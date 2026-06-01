import re

from attack_classifier.result import AttackClassificationResult
from attack_classifier.pattern_loader import PatternLoader
from attack_classifier.scoring import ConfidenceScorer


KEYWORD_WEIGHT_RATIO = 0.4

SESSION_MULTI_TURN_THRESHOLD = 2
SESSION_PROBE_CATEGORIES = {
    "partial_disclosure", "encoding_bypass", "translation_bypass", "direct_request",
}


class AttackClassifier:
    def __init__(
        self,
        attacks_path: str = None,
        patterns_path: str = None,
    ):
        self.attacks_path = attacks_path
        self.patterns_path = patterns_path
        self.attacks = []
        self.patterns = []
        self.attack_map = {}
        self._loaded = False

    def _ensure_loaded(self):
        if self._loaded:
            return
        if self.attacks_path and self.patterns_path:
            self.attacks = PatternLoader.load_attacks(self.attacks_path)
            self.patterns = PatternLoader.load_attack_patterns(self.patterns_path)
            self.attack_map = PatternLoader.build_attack_map(self.attacks)
        self._loaded = True

    def classify(
        self,
        prompt: str,
        normalized_prompt: str | None = None,
        input_guard_result: dict | None = None,
        session_context: dict | None = None,
    ) -> AttackClassificationResult:
        self._ensure_loaded()

        if not prompt or not prompt.strip():
            return AttackClassificationResult(
                is_attack=False,
                primary_category="benign",
            )

        text = (normalized_prompt or prompt).lower()
        category_matches: dict[str, list[dict]] = {}
        category_weights: dict[str, list[float]] = {}
        category_match_details: dict[str, list[dict]] = {}
        all_evidence = []

        for rule in self.patterns:
            match_info = self._match_rule(rule, text)
            if match_info["matched"]:
                cat = rule["category"]
                if cat not in category_matches:
                    category_matches[cat] = []
                    category_weights[cat] = []
                    category_match_details[cat] = []
                category_matches[cat].append(rule)
                category_weights[cat].extend(match_info["effective_weights"])
                all_evidence.extend(match_info["fragments"])

                for i, frag in enumerate(match_info["fragments"]):
                    category_match_details[cat].append({
                        "fragment": frag,
                        "match_type": match_info["match_types"][i] if i < len(match_info["match_types"]) else "unknown",
                    })

        session_rules = self._analyze_session_context(session_context)
        for srule in session_rules:
            cat = srule["category"]
            if cat not in category_matches:
                category_matches[cat] = []
                category_weights[cat] = []
                category_match_details[cat] = []
            category_matches[cat].append(srule)
            category_weights[cat].append(srule.get("weight", 0.0))
            all_evidence.append(srule.get("reason", ""))

        if not category_matches:
            return AttackClassificationResult(
                is_attack=False,
                primary_category="benign",
            )

        category_scores = {}
        all_matched_rules = []
        matched_categories = []

        for cat in category_matches:
            rules = category_matches[cat]
            weights = category_weights[cat]
            attack_def = self.attack_map.get(cat, {})
            base_confidence = attack_def.get("base_confidence", 0.5)
            score = ConfidenceScorer.compute_category_score(base_confidence, weights)
            category_scores[cat] = score
            matched_categories.append(cat)
            for rule in rules:
                fragments = [d["fragment"] for d in category_match_details.get(cat, [])]
                all_matched_rules.append({
                    "rule_id": rule.get("rule_id", ""),
                    "category": cat,
                    "severity_hint": rule.get("severity_hint", "low"),
                    "weight": rule.get("weight", 0.0),
                    "reason": rule.get("reason", ""),
                    "matched_fragments": fragments,
                })

        primary = ConfidenceScorer.pick_primary_category(category_scores, category_matches)
        final_confidence = category_scores[primary]

        attack_def = self.attack_map.get(primary, {})
        severity_hint = ConfidenceScorer.compute_severity_hint(
            all_matched_rules, primary, self.attack_map
        )
        recommended_skill = attack_def.get("recommended_skill")
        notes = attack_def.get("description", "")

        return AttackClassificationResult(
            is_attack=True,
            primary_category=primary,
            matched_categories=matched_categories,
            confidence=round(final_confidence, 2),
            severity_hint=severity_hint,
            matched_rules=all_matched_rules,
            evidence=list(set(all_evidence)),
            recommended_skill=recommended_skill,
            notes=notes,
        )

    def _analyze_session_context(self, session_context: dict | None) -> list[dict]:
        if not session_context:
            return []

        turn_count = session_context.get("turn_count", 0)
        previous_categories = session_context.get("previous_categories", [])

        if turn_count < 2:
            return []

        if not previous_categories:
            return []

        probe_count = sum(
            1 for c in previous_categories if c in SESSION_PROBE_CATEGORIES
        )

        if probe_count >= SESSION_MULTI_TURN_THRESHOLD:
            return [
                {
                    "rule_id": "SESSION_MULTI_TURN_001",
                    "category": "multi_turn_probe",
                    "severity_hint": "high",
                    "weight": 0.4,
                    "reason": "Repeated probing behavior detected from session context.",
                },
            ]

        return []

    def _match_rule(self, rule: dict, text: str) -> dict:
        fragments = []
        effective_weights = []
        match_types = []
        matched = False

        full_weight = rule.get("weight", 0.0)
        kw_weight = full_weight * KEYWORD_WEIGHT_RATIO

        for kw in rule.get("keywords", []):
            try:
                if re.search(r"\b" + re.escape(kw.lower()) + r"\b", text):
                    fragments.append(kw)
                    effective_weights.append(kw_weight)
                    match_types.append("keyword")
                    matched = True
            except re.error:
                if kw.lower() in text:
                    fragments.append(kw)
                    effective_weights.append(kw_weight)
                    match_types.append("keyword")
                    matched = True

        for phrase in rule.get("phrases", []):
            if phrase.lower() in text:
                fragments.append(phrase)
                effective_weights.append(full_weight)
                match_types.append("phrase")
                matched = True

        for regex in rule.get("regex", []):
            try:
                if re.search(regex, text):
                    fragments.append(regex)
                    effective_weights.append(full_weight)
                    match_types.append("regex")
                    matched = True
            except re.error:
                continue

        return {
            "matched": matched,
            "fragments": fragments,
            "effective_weights": effective_weights,
            "match_types": match_types,
        }
