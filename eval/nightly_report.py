"""Nightly report generator for ARGOS.

This script reads logs or metrics snapshots from the specified directory and
computes summary statistics (Support‑Weighted Accuracy, No‑Evidence Rate,
Contradiction Rate, Expected Calibration Error).  It then writes a simple
HTML report to the given output path.  The report can be served via a
static web server or viewed directly in a browser.

Usage:
    python nightly_report.py --logs ./logs --output ./eval/report.html
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .metrics import (
    support_weighted_accuracy,
    no_evidence_rate,
    contradiction_rate,
    calibration_error,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate nightly ARGOS report")
    parser.add_argument("--logs", type=str, required=True, help="Directory containing metrics snapshots")
    parser.add_argument(
        "--output", type=str, default="report.html", help="Path to write the HTML report"
    )
    return parser.parse_args()


def load_snapshots(log_dir: Path) -> List[Dict[str, Any]]:
    """Load metrics snapshot JSON files from the log directory."""
    snapshots = []
    if not log_dir.exists():
        return snapshots
    for file in log_dir.glob("*.json"):
        try:
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                snapshots.append(data)
        except Exception:
            continue
    return snapshots


def aggregate_metrics(snapshots: List[Dict[str, Any]]) -> Dict[str, float]:
    """Aggregate metrics across snapshots by averaging their values."""
    if not snapshots:
        return {"swa": 0.0, "ner": 0.0, "cr": 0.0, "ece": 0.0}
    swa = sum(s.get("support_rate", 0.0) for s in snapshots) / len(snapshots)
    ner = sum(s.get("ner", 0.0) for s in snapshots) / len(snapshots)
    cr = sum(s.get("cr", 0.0) for s in snapshots) / len(snapshots)
    ece = sum(s.get("ece", 0.0) for s in snapshots) / len(snapshots)
    return {"swa": swa, "ner": ner, "cr": cr, "ece": ece}


def write_html_report(agg: Dict[str, float], output_path: Path) -> None:
    """Write an HTML report summarising the metrics."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    html = f"""
    <html>
      <head>
        <title>ARGOS Nightly Report</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 2rem; }}
          h1 {{ color: #2d3748; }}
          table {{ border-collapse: collapse; margin-top: 1rem; }}
          th, td {{ border: 1px solid #cbd5e0; padding: 0.5rem 1rem; text-align: left; }}
          th {{ background-color: #e2e8f0; }}
        </style>
      </head>
      <body>
        <h1>ARGOS Nightly Metrics Report</h1>
        <p>Generated: {now}</p>
        <table>
          <tr><th>Metric</th><th>Value</th></tr>
          <tr><td>Support‑Weighted Accuracy (SWA)</td><td>{agg['swa']:.3f}</td></tr>
          <tr><td>No‑Evidence Rate (NER)</td><td>{agg['ner']:.3f}</td></tr>
          <tr><td>Contradiction Rate (CR)</td><td>{agg['cr']:.3f}</td></tr>
          <tr><td>Expected Calibration Error (ECE)</td><td>{agg['ece']:.3f}</td></tr>
        </table>
      </body>
    </html>
    """
    output_path.write_text(html, encoding="utf-8")


def main() -> None:
    args = parse_args()
    log_dir = Path(args.logs)
    snapshots = load_snapshots(log_dir)
    agg = aggregate_metrics(snapshots)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_html_report(agg, output_path)
    print(f"[nightly_report] Wrote report to {output_path}")


if __name__ == "__main__":
    main()