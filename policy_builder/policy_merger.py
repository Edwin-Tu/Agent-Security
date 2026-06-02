from __future__ import annotations


def merge_skill_defense_results(
    enabled_skills: list[str],
    skill_defense_results: list[dict],
) -> dict:
    deduped_skills = list(dict.fromkeys(enabled_skills))
    blocked_transformations: list[str] = []
    verify_encoding = False
    verify_reconstruction = False
    runtime_monitoring_mode = "normal"
    skill_runtime_modes: list[str] = []

    for result in skill_defense_results:
        transformations = result.get("blocked_transformations", [])
        for t in transformations:
            if t not in blocked_transformations:
                blocked_transformations.append(t)

        if result.get("verify_encoding"):
            verify_encoding = True

        if result.get("verify_reconstruction"):
            verify_reconstruction = True

        mode = result.get("runtime_monitoring_mode")
        if mode:
            skill_runtime_modes.append(mode)

    if "strict" in skill_runtime_modes:
        runtime_monitoring_mode = "strict"

    return {
        "enabled_skills": deduped_skills,
        "blocked_transformations": blocked_transformations,
        "verify_encoding": verify_encoding,
        "verify_reconstruction": verify_reconstruction,
        "runtime_monitoring_mode": runtime_monitoring_mode,
    }
