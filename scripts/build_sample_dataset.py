from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar, cast


NORMAL_SOURCE = "normal_prompts_50k"
JAILBREAK_SOURCE = "SLM_injection_relabelled"


class DatasetError(Exception):
    pass


@dataclass(frozen=True)
class NormalCandidate:
    prompt: str
    original_id: str | None


@dataclass(frozen=True)
class JailbreakCandidate:
    prompt: str
    original_row: int


CandidateT = TypeVar("CandidateT")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a balanced sample dataset as JSONL")
    _ = parser.add_argument("--normal-input", required=True, help="Path to normal prompts JSONL")
    _ = parser.add_argument("--jailbreak-input", required=True, help="Path to jailbreak prompts CSV")
    _ = parser.add_argument("--output", default="sampled_prompts_50.jsonl", help="Output JSONL path")
    _ = parser.add_argument("--normal-count", type=int, default=25, help="Number of normal prompts to sample")
    _ = parser.add_argument("--jailbreak-count", type=int, default=25, help="Number of jailbreak prompts to sample")
    _ = parser.add_argument("--seed", type=int, default=42, help="Deterministic sampling seed")
    _ = parser.add_argument(
        "--jailbreak-format",
        choices=("auto", "csv"),
        default="auto",
        help="Jailbreak input format",
    )
    return parser


def _ensure_file_exists(path: Path, label: str) -> None:
    if not path.is_file():
        raise DatasetError(f"{label} not found: {path}")


def _ensure_output_parent_exists(path: Path) -> None:
    parent = path.parent
    if parent != Path(".") and not parent.exists():
        raise DatasetError(f"Output directory does not exist: {parent}")


def _validate_positive_count(value: int, flag_name: str) -> None:
    if value <= 0:
        raise DatasetError(f"{flag_name} must be greater than 0")


def _normalize_original_id(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _read_normal_candidates(path: Path) -> tuple[list[NormalCandidate], int]:
    candidates: list[NormalCandidate] = []
    skipped_empty_prompts = 0
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                skipped_empty_prompts += 1
                continue
            try:
                record_data = cast(object, json.loads(line))
            except json.JSONDecodeError as exc:
                raise DatasetError(f"Invalid JSONL in {path} at line {line_number}: {exc.msg}") from exc
            if not isinstance(record_data, dict):
                raise DatasetError(f"Normal input must contain JSON objects in {path} at line {line_number}")
            record = cast(dict[str, object], record_data)
            prompt = record.get("prompt")
            prompt_text = "" if prompt is None else str(prompt).strip()
            if not prompt_text:
                skipped_empty_prompts += 1
                continue
            candidates.append(NormalCandidate(prompt=prompt_text, original_id=_normalize_original_id(record.get("id"))))
    return candidates, skipped_empty_prompts


def _normalize_jailbreak_label(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value is True
    if isinstance(value, (int, float)):
        return float(value) == 1.0
    text = str(value).strip()
    if not text:
        return False
    try:
        return float(text) == 1.0
    except ValueError:
        return False


def _read_jailbreak_candidates(path: Path) -> tuple[list[JailbreakCandidate], int, int]:
    candidates: list[JailbreakCandidate] = []
    skipped_empty_prompts = 0
    skipped_non_attack_rows = 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        first_row = next(reader, None)
        if first_row is None:
            return candidates, skipped_empty_prompts, skipped_non_attack_rows

        rows: list[list[str]] = []
        header_present = len(first_row) >= 3 and first_row[1].strip() == "Prompt" and first_row[2].strip() == "Label"
        if not header_present:
            rows.append(first_row)

        rows.extend(reader)

        start_row_number = 2 if header_present else 1
        for row_number, row in enumerate(rows, start=start_row_number):
            prompt = row[1].strip() if len(row) > 1 else ""
            if not prompt:
                skipped_empty_prompts += 1
                continue
            label_value = row[2] if len(row) > 2 else None
            if not _normalize_jailbreak_label(label_value):
                skipped_non_attack_rows += 1
                continue
            candidates.append(JailbreakCandidate(prompt=prompt, original_row=row_number))
    return candidates, skipped_empty_prompts, skipped_non_attack_rows


def _sample_candidates(candidates: list[CandidateT], count: int, rng: random.Random, kind: str) -> list[CandidateT]:
    if len(candidates) < count:
        raise DatasetError(f"Fewer valid {kind} candidates than requested: have {len(candidates)}, need {count}")
    return rng.sample(candidates, count)


def _build_normal_records(samples: list[NormalCandidate]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for index, sample in enumerate(samples, start=1):
        records.append(
            {
                "id": f"sample_normal_{index:04d}",
                "prompt": sample.prompt,
                "label": "normal",
                "is_injection": False,
                "should_block": False,
                "source": NORMAL_SOURCE,
                "sample_type": "normal",
                "original_id": sample.original_id,
                "original_row": None,
            }
        )
    return records


def _build_jailbreak_records(samples: list[JailbreakCandidate]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for index, sample in enumerate(samples, start=1):
        records.append(
            {
                "id": f"sample_jailbreak_{index:04d}",
                "prompt": sample.prompt,
                "label": "jailbreak",
                "is_injection": True,
                "should_block": True,
                "source": JAILBREAK_SOURCE,
                "sample_type": "jailbreak",
                "original_id": None,
                "original_row": sample.original_row,
            }
        )
    return records


def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            _ = handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _emit_summary(*, normal_candidates: int, jailbreak_candidates: int, sampled_normal: int, sampled_jailbreak: int, skipped_empty_prompts: int, skipped_non_attack_rows: int, output: Path) -> None:
    print(
        " ".join(
            [
                f"normal_candidates={normal_candidates}",
                f"jailbreak_candidates={jailbreak_candidates}",
                f"sampled_normal={sampled_normal}",
                f"sampled_jailbreak={sampled_jailbreak}",
                f"skipped_empty_prompts={skipped_empty_prompts}",
                f"skipped_non_attack_rows={skipped_non_attack_rows}",
                f"output={output}",
            ]
        ),
        file=sys.stderr,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    try:
        normal_input = Path(cast(str, args.normal_input))
        jailbreak_input = Path(cast(str, args.jailbreak_input))
        output_path = Path(cast(str, args.output))
        normal_count = cast(int, args.normal_count)
        jailbreak_count = cast(int, args.jailbreak_count)
        _validate_positive_count(normal_count, "normal-count")
        _validate_positive_count(jailbreak_count, "jailbreak-count")
        _ensure_file_exists(normal_input, "Normal input")
        _ensure_file_exists(jailbreak_input, "Jailbreak input")
        _ensure_output_parent_exists(output_path)

        normal_candidates, skipped_empty_normal = _read_normal_candidates(normal_input)
        jailbreak_candidates, skipped_empty_jailbreak, skipped_non_attack_rows = _read_jailbreak_candidates(jailbreak_input)

        rng = random.Random(cast(int, args.seed))
        normal_samples = _sample_candidates(normal_candidates, normal_count, rng, "normal")
        jailbreak_samples = _sample_candidates(jailbreak_candidates, jailbreak_count, rng, "jailbreak")

        records = _build_normal_records(normal_samples) + _build_jailbreak_records(jailbreak_samples)
        _write_jsonl(output_path, records)

        _emit_summary(
            normal_candidates=len(normal_candidates),
            jailbreak_candidates=len(jailbreak_candidates),
            sampled_normal=len(normal_samples),
            sampled_jailbreak=len(jailbreak_samples),
            skipped_empty_prompts=skipped_empty_normal + skipped_empty_jailbreak,
            skipped_non_attack_rows=skipped_non_attack_rows,
            output=output_path,
        )
        return 0
    except DatasetError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
