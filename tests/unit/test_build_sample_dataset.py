from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import pytest

from scripts import build_sample_dataset as sampler


FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
NORMAL_FIXTURE = FIXTURES_DIR / "normal_prompts_fixture.jsonl"
JAILBREAK_FIXTURE = FIXTURES_DIR / "jailbreak_prompts_fixture.csv"
JAILBREAK_TOO_FEW_FIXTURE = FIXTURES_DIR / "jailbreak_too_few.csv"

EXPECTED_KEYS = {
    "id",
    "prompt",
    "label",
    "is_injection",
    "should_block",
    "source",
    "sample_type",
    "original_id",
    "original_row",
}


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _run_sampler(output_path: Path, *, normal_input: Path = NORMAL_FIXTURE, jailbreak_input: Path = JAILBREAK_FIXTURE, seed: int = 42, normal_count: int = 25, jailbreak_count: int = 25) -> int:
    return sampler.main(
        [
            "--normal-input",
            str(normal_input),
            "--jailbreak-input",
            str(jailbreak_input),
            "--output",
            str(output_path),
            "--seed",
            str(seed),
            "--normal-count",
            str(normal_count),
            "--jailbreak-count",
            str(jailbreak_count),
        ]
    )


def test_default_sample_is_deterministic_balanced_and_schema_valid(tmp_path: Path) -> None:
    first_output = tmp_path / "sample-1.jsonl"
    second_output = tmp_path / "sample-2.jsonl"

    assert _run_sampler(first_output) == 0
    assert _run_sampler(second_output) == 0

    first_bytes = first_output.read_bytes()
    second_bytes = second_output.read_bytes()
    assert first_bytes == second_bytes

    records = _read_jsonl(first_output)
    assert len(records) == 50
    assert sum(record["sample_type"] == "normal" for record in records) == 25
    assert sum(record["sample_type"] == "jailbreak" for record in records) == 25
    assert all(cast(str, record["prompt"]).strip() for record in records)
    assert all(set(record) == EXPECTED_KEYS for record in records)

    normal_records = [record for record in records if record["sample_type"] == "normal"]
    jailbreak_records = [record for record in records if record["sample_type"] == "jailbreak"]

    assert all(record["label"] == "normal" for record in normal_records)
    assert all(record["is_injection"] is False for record in normal_records)
    assert all(record["should_block"] is False for record in normal_records)
    assert all(record["source"] == sampler.NORMAL_SOURCE for record in normal_records)

    assert all(record["label"] == "jailbreak" for record in jailbreak_records)
    assert all(record["is_injection"] is True for record in jailbreak_records)
    assert all(record["should_block"] is True for record in jailbreak_records)
    assert all(record["source"] == sampler.JAILBREAK_SOURCE for record in jailbreak_records)

    excluded_prompts = {"excluded prompt 31", "excluded prompt 32", "excluded prompt 33", "excluded prompt 34", "excluded prompt 35"}
    output_prompts = {str(record["prompt"]) for record in records}
    assert excluded_prompts.isdisjoint(output_prompts)


def test_different_seed_changes_sample_output(tmp_path: Path) -> None:
    first_output = tmp_path / "sample-seed-41.jsonl"
    second_output = tmp_path / "sample-seed-42.jsonl"

    assert _run_sampler(first_output, seed=41) == 0
    assert _run_sampler(second_output, seed=42) == 0

    assert first_output.read_text(encoding="utf-8") != second_output.read_text(encoding="utf-8")


def test_missing_prompt_normal_row_is_skipped(tmp_path: Path) -> None:
    output_path = tmp_path / "sample-30-normal.jsonl"

    assert _run_sampler(output_path, normal_count=30) == 0

    records = _read_jsonl(output_path)
    assert len(records) == 55
    assert sum(record["sample_type"] == "normal" for record in records) == 30
    assert sum(record["sample_type"] == "jailbreak" for record in records) == 25
    assert all(cast(str, record["prompt"]).strip() for record in records)


def test_malformed_jsonl_returns_cli_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    malformed_input = tmp_path / "malformed.jsonl"
    _ = malformed_input.write_text('{"id":"ok","prompt":"good"}\nnot-json\n', encoding="utf-8")
    output_path = tmp_path / "out.jsonl"

    exit_code = _run_sampler(output_path, normal_input=malformed_input)

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Invalid JSONL" in captured.err


def test_missing_input_path_exits_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    missing_input = tmp_path / "missing-normal.jsonl"
    output_path = tmp_path / "out.jsonl"

    exit_code = _run_sampler(output_path, normal_input=missing_input)

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "not found" in captured.err


def test_insufficient_jailbreak_candidates_exits_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    output_path = tmp_path / "out.jsonl"

    exit_code = _run_sampler(output_path, jailbreak_input=JAILBREAK_TOO_FEW_FIXTURE)

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Fewer valid jailbreak candidates" in captured.err


@pytest.mark.parametrize(
    ("normal_count", "jailbreak_count", "expected_message"),
    [
        (-1, 25, "normal-count must be greater than 0"),
        (25, -1, "jailbreak-count must be greater than 0"),
        (0, 25, "normal-count must be greater than 0"),
        (25, 0, "jailbreak-count must be greater than 0"),
    ],
)
def test_non_positive_counts_exit_two(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    normal_count: int,
    jailbreak_count: int,
    expected_message: str,
) -> None:
    output_path = tmp_path / "out.jsonl"

    exit_code = _run_sampler(output_path, normal_count=normal_count, jailbreak_count=jailbreak_count)

    captured = capsys.readouterr()
    assert exit_code == 2
    assert expected_message in captured.err
    assert "Traceback" not in captured.err
