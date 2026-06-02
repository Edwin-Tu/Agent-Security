import os

from risk_scoring.risk_scoring_engine import RiskScoringEngine


def test_loads_default_rules_when_json_path_missing():
    engine = RiskScoringEngine(rules_path="nonexistent_rules.json")

    assert engine.fallback_to_default_rules is True
    assert engine.rules["attack_category_scores"]["benign"] == 0
    assert engine.rules["asset_risk_scores"]["critical"] == 50


def test_loads_default_rules_when_json_invalid(tmp_path):
    bad_file = tmp_path / "broken.json"
    bad_file.write_text("{ invalid json }", encoding="utf-8")

    engine = RiskScoringEngine(rules_path=str(bad_file))

    assert engine.fallback_to_default_rules is True
    assert engine.rules["match_type_scores"]["exact_match"] == 40
