"""
Multi-format report generation.

Produces JSON (machine-readable), CSV (spreadsheet-friendly), and
a self-contained HTML dashboard (human-readable) so results can be
shared with reviewers, auditors, and portfolio readers alike.
"""

import csv
import json
from pathlib import Path
from datetime import datetime

from . import config


def _ensure_dir() -> None:
    """Create the report output directory if it does not exist."""
    config.REPORT_DIR.mkdir(parents=True, exist_ok=True)


def write_json(results: list, host: str) -> Path:
    """Export scan results to a structured JSON file."""
    _ensure_dir()
    path = config.REPORT_DIR / f"scan_{host}_{_stamp()}.json"
    payload = {
        "host": host,
        "scanned_at": datetime.now().isoformat(),
        "open_ports": [r.as_dict() for r in results],
    }
    path.write_text(json.dumps(payload, indent=2))
    return path


def write_csv(results: list, host: str) -> Path:
    """Export scan results to a CSV file (spreadsheet-friendly)."""
    _ensure_dir()
    path = config.REPORT_DIR / f"scan_{host}_{_stamp()}.csv"
    fieldnames = ["port", "service", "banner", "latency_ms"]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r.as_dict())
    return path


def write_html(results: list, host: str) -> Path:
    """Minimal, dependency-free HTML dashboard for human review."""
    _ensure_dir()
    path = config.REPORT_DIR / f"scan_{host}_{_stamp()}.html"
    rows = "".join(
        f"<tr><td>{r.port}</td><td>{r.service}</td>"
        f"<td>{r.banner or 'N/A'}</td><td>{r.latency_ms:.2f}</td></tr>"
        for r in results
    )
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Port Scan — {host}</title><style>
body{{font-family:Segoe UI,Arial;margin:40px;background:#f5f7fb}}
table{{border-collapse:collapse;width:100%;background:#fff;box-shadow:0 2px 8px #d5dbe6}}
th{{background:#1f2937;color:#fff;padding:12px;text-align:left}}
td{{padding:10px;border-bottom:1px solid #e5e7eb}}
</style></head><body>
<h1>Port Scan Report</h1>
<p><b>Target:</b> {host}</p>
<p><b>Generated:</b> {datetime.now()}</p>
<p><b>Open ports:</b> {len(results)}</p>
<table><tr><th>Port</th><th>Service</th><th>Banner</th><th>Latency (ms)</th></tr>
{rows}</table></body></html>"""
    path.write_text(html, encoding="utf-8")
    return path


def _stamp() -> str:
    """Return a timestamp string for unique report filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
