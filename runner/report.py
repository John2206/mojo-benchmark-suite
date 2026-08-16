#!/usr/bin/env python3
"""Renders a results/*.json file as a static HTML page with a bar chart
per benchmark.

Usage:
    python3 runner/report.py [results/file.json] [-o report.html]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from languages import ROOT

RESULTS_DIR = ROOT / "results"

COLORS = {
    "C": "#5b8dee",
    "Rust": "#e07b39",
    "Java": "#c0392b",
    "Python": "#3572A5",
    "Mojo": "#ff6b35",
}
DEFAULT_COLOR = "#888888"

CHART_WIDTH = 500
BAR_HEIGHT = 28
BAR_GAP = 8


def latest_results_file() -> Path:
    files = sorted(RESULTS_DIR.glob("*.json"))
    if not files:
        sys.exit("No results/*.json files found — run with --json first.")
    return files[-1]


def render_chart(entry: dict) -> str:
    rows = sorted(entry["results"], key=lambda r: r["min"])
    if not rows:
        return "<p><em>no results</em></p>"
    max_time = max(r["min"] for r in rows)
    height = len(rows) * (BAR_HEIGHT + BAR_GAP)

    bars = []
    for i, row in enumerate(rows):
        y = i * (BAR_HEIGHT + BAR_GAP)
        width = max(row["min"] / max_time * CHART_WIDTH, 2)
        color = COLORS.get(row["language"], DEFAULT_COLOR)
        bars.append(
            f'<rect x="120" y="{y}" width="{width:.1f}" height="{BAR_HEIGHT}" fill="{color}" />'
            f'<text x="110" y="{y + BAR_HEIGHT / 2 + 5}" text-anchor="end" font-size="13">{row["language"]}</text>'
            f'<text x="{120 + width + 6:.1f}" y="{y + BAR_HEIGHT / 2 + 5}" font-size="12" fill="#555">{row["min"]:.4f}s</text>'
        )

    return f'<svg width="{120 + CHART_WIDTH + 80}" height="{height}">{"".join(bars)}</svg>'


def render_html(data: list[dict]) -> str:
    sections = []
    for entry in data:
        sections.append(
            f'<h2>{entry["benchmark"]} <small>(size={entry["size"]})</small></h2>\n'
            f'{render_chart(entry)}'
        )
    body = "\n".join(sections)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Benchmark results</title>
<style>
body {{ font-family: sans-serif; max-width: 800px; margin: 2rem auto; }}
h2 {{ margin-top: 2.5rem; }}
small {{ color: #888; font-weight: normal; }}
</style>
</head>
<body>
<h1>Benchmark results</h1>
{body}
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_file", nargs="?", default=None)
    parser.add_argument("-o", "--output", default="report.html")
    args = parser.parse_args()

    path = Path(args.results_file) if args.results_file else latest_results_file()
    data = json.loads(path.read_text())

    out_path = ROOT / args.output
    out_path.write_text(render_html(data))
    print(f"Wrote {out_path.relative_to(ROOT)} from {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
