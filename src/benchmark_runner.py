"""Benchmark runner for SecretGuard."""

from __future__ import annotations

from .input_guard import InputGuard


class BenchmarkRunner:
    """Run simple attack and safe prompt examples through the input guard."""

    def __init__(self, input_guard: InputGuard | None = None):
        self.input_guard = input_guard or InputGuard()

    def run(self, prompts: list[str]) -> dict:
        results = []
        blocked = 0

        for prompt in prompts:
            result = self.input_guard.inspect(prompt)
            if result["blocked"]:
                blocked += 1
            results.append(result)

        return {
            "total_events": len(results),
            "blocked": blocked,
            "items": [
                {
                    "label": prompt[:50],
                    "level": result["level"],
                    "action": result["action"],
                    "blocked": result["blocked"],
                }
                for prompt, result in zip(prompts, results)
            ],
        }
