from prompt_builder.asset_redactor import AssetRedactor


def test_redact_removes_value():
    redactor = AssetRedactor()
    asset = {
        "asset_id": "secret_001",
        "name": "比賽 flag",
        "type": "flag",
        "value": "picoCTF{real_secret_flag}",
        "risk_level": "high",
        "protection_modes": ["exact_match", "partial_match"],
    }
    result = redactor.redact(asset)
    assert "picoCTF{real_secret_flag}" not in str(result)
    assert result["asset_ref"] == "secret_001"
    assert result["type"] == "flag"
    assert result["risk_level"] == "high"
    assert result["protection_modes"] == ["exact_match", "partial_match"]


def test_redact_preserves_asset_ref():
    redactor = AssetRedactor()
    asset = {
        "asset_id": "secret_002",
        "type": "api_key",
        "value": "sk-xxxxxxxxxxxxxxxx",
        "risk_level": "critical",
        "protection_modes": [],
    }
    result = redactor.redact(asset)
    assert result["asset_ref"] == "secret_002"


def test_redact_preserves_type_risk_protection():
    redactor = AssetRedactor()
    asset = {
        "asset_id": "secret_003",
        "type": "password",
        "value": "SuperSecretP@ss",
        "risk_level": "medium",
        "protection_modes": ["exact_match"],
    }
    result = redactor.redact(asset)
    assert result["type"] == "password"
    assert result["risk_level"] == "medium"
    assert result["protection_modes"] == ["exact_match"]


def test_redact_multiple_assets():
    redactor = AssetRedactor()
    assets = [
        {
            "asset_id": "secret_001",
            "type": "flag",
            "value": "picoCTF{flag1}",
            "risk_level": "high",
            "protection_modes": ["exact_match"],
        },
        {
            "asset_id": "secret_002",
            "type": "api_key",
            "value": "sk-xxxxxx",
            "risk_level": "critical",
            "protection_modes": ["exact_match", "partial_match"],
        },
    ]
    results = redactor.redact_all(assets)
    assert len(results) == 2
    assert results[0]["asset_ref"] == "secret_001"
    assert results[1]["asset_ref"] == "secret_002"
    assert "picoCTF{flag1}" not in str(results)
    assert "sk-xxxxxx" not in str(results)


def test_redact_missing_fields():
    redactor = AssetRedactor()
    asset = {"asset_id": "secret_004", "value": "some_value"}
    result = redactor.redact(asset)
    assert result["asset_ref"] == "secret_004"
    assert "some_value" not in str(result)


def test_redact_empty_assets():
    redactor = AssetRedactor()
    results = redactor.redact_all([])
    assert results == []
