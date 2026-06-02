import json
import time
from pathlib import Path
from datetime import datetime, timezone


class Evaluator:
    def __init__(self, results_dir: str = None):
        self.results_dir = results_dir or str(Path(__file__).parent / "results")
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        self.results: list[dict] = []

    def run_test(self, name: str, fn, *args, **kwargs) -> dict:
        start = time.time()
        try:
            output = fn(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            output = None
            success = False
            error = str(e)
        elapsed = time.time() - start
        result = {"name": name, "success": success, "elapsed": round(elapsed, 4), "error": error, "output": output, "timestamp": datetime.now(timezone.utc).isoformat()}
        self.results.append(result)
        return result

    def summary(self) -> dict:
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        return {"total": total, "passed": passed, "failed": total - passed, "pass_rate": round(passed / max(total, 1), 3), "total_time": round(sum(r["elapsed"] for r in self.results), 4)}

    def save(self, filename: str = None) -> str:
        if filename is None:
            filename = f"benchmark_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        path = Path(self.results_dir) / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"results": self.results, "summary": self.summary()}, f, ensure_ascii=False, indent=2)
        return str(path)
