import json
import html
from pathlib import Path
from datetime import datetime, timezone


class ReportGenerator:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or str(Path(__file__).parent)

    def generate_from_log(self, log_path: str) -> dict:
        path = Path(log_path)
        if not path.exists():
            return {"error": "Log file not found."}
        events = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return self._build_report(events)

    def _build_report(self, events: list[dict]) -> dict:
        total = len(events)
        blocked = sum(1 for e in events if e.get("blocked", False))
        actions = {}
        for e in events:
            a = e.get("policy_action", "unknown")
            actions[a] = actions.get(a, 0) + 1
        return {
            "report_time": datetime.now(timezone.utc).isoformat(),
            "total_events": total,
            "blocked_events": blocked,
            "block_rate": round(blocked / max(total, 1), 3),
            "action_distribution": actions,
            "events": events,
        }

    def generate_html(self, report: dict) -> str:
        lines = ["<!DOCTYPE html><html><head><meta charset='utf-8'>",
                 "<title>SecretGuard Report</title>",
                 "<style>body{font-family:sans-serif;margin:20px}",
                 "table{border-collapse:collapse;width:100%}",
                 "th,td{border:1px solid #ddd;padding:8px;text-align:left}",
                 "th{background:#4CAF50;color:white}</style></head><body>",
                 f"<h1>SecretGuard Report</h1>",
                 f"<p>Generated: {report.get('report_time', '')}</p>",
                 f"<p>Total Events: {report.get('total_events', 0)}</p>",
                 f"<p>Blocked Events: {report.get('blocked_events', 0)}</p>",
                 f"<p>Block Rate: {report.get('block_rate', 0)}</p>",
                 "<h2>Action Distribution</h2><table><tr><th>Action</th><th>Count</th></tr>"]
        for action, count in report.get("action_distribution", {}).items():
            lines.append(f"<tr><td>{html.escape(action)}</td><td>{count}</td></tr>")
        lines.append("</table>")
        if report.get("events"):
            lines.append("<h2>Events</h2><table><tr><th>Timestamp</th><th>Type</th><th>Action</th><th>Blocked</th></tr>")
            for e in report["events"][-50:]:
                lines.append(f"<tr><td>{html.escape(str(e.get('timestamp','')))}</td>"
                             f"<td>{html.escape(str(e.get('type','')))}</td>"
                             f"<td>{html.escape(str(e.get('policy_action','')))}</td>"
                             f"<td>{e.get('blocked', False)}</td></tr>")
            lines.append("</table>")
        lines.append("</body></html>")
        return "\n".join(lines)

    def generate_markdown(self, report: dict) -> str:
        lines = ["# SecretGuard Report\n",
                 f"**Generated**: {report.get('report_time', '')}\n",
                 f"**Total Events**: {report.get('total_events', 0)}",
                 f"**Blocked Events**: {report.get('blocked_events', 0)}",
                 f"**Block Rate**: {report.get('block_rate', 0)}\n",
                 "## Action Distribution\n",
                 "| Action | Count |",
                 "|--------|-------|"]
        for action, count in report.get("action_distribution", {}).items():
            lines.append(f"| {action} | {count} |")
        return "\n".join(lines)

    def generate_benchmark_summary(self, benchmark_results: dict) -> str:
        lines = ["# Benchmark Summary\n",
                 f"**Total Tests**: {benchmark_results.get('total', 0)}",
                 f"**Passed**: {benchmark_results.get('passed', 0)}",
                 f"**Failed**: {benchmark_results.get('failed', 0)}",
                 f"**Pass Rate**: {benchmark_results.get('pass_rate', 0)*100:.1f}%",
                 f"**Total Time**: {benchmark_results.get('total_time', 0):.4f}s\n"]
        return "\n".join(lines)

    def generate_leakage_statistics(self, events: list[dict]) -> dict:
        total = len(events)
        leak_events = [e for e in events if e.get("leaked", False)]
        leak_types = {}
        for e in leak_events:
            lt = e.get("leak_type", "unknown")
            leak_types[lt] = leak_types.get(lt, 0) + 1
        return {
            "total_events": total,
            "leak_events": len(leak_events),
            "leak_rate": round(len(leak_events) / max(total, 1), 3),
            "leak_type_distribution": leak_types,
        }

    def save_report(self, report: dict, filename: str = None) -> str:
        if filename is None:
            filename = f"report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        path = Path(self.output_dir) / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return str(path)

    def save_html(self, report: dict, filename: str = None) -> str:
        if filename is None:
            filename = f"report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.html"
        path = Path(self.output_dir) / filename
        html_content = self.generate_html(report)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return str(path)

    def save_markdown(self, report: dict, filename: str = None) -> str:
        if filename is None:
            filename = f"report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
        path = Path(self.output_dir) / filename
        md_content = self.generate_markdown(report)
        with open(path, "w", encoding="utf-8") as f:
            f.write(md_content)
        return str(path)
