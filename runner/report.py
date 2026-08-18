#!/usr/bin/env python3
"""Renders a results/*.json file as a static HTML page with a bar chart
per benchmark.

Usage:
    python3 runner/report.py [results/file.json] [-o report.html]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import stats
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

# stdev/mean above this is flagged "(noisy)" in the summary table.
NOISY_CV_THRESHOLD = 0.10


def latest_results_file() -> Path:
    files = sorted(RESULTS_DIR.glob("*.json"))
    if not files:
        sys.exit("No results/*.json files found — run with --json first.")
    return files[-1]


def render_chart(entry: dict, metric: str, fmt: str, unit: str, title: str = "") -> str:
    rows = sorted((r for r in entry["results"] if r.get(metric) is not None), key=lambda r: r[metric])
    if not rows:
        return "<p><em>no data</em></p>"
    max_value = max(r[metric] for r in rows)
    pad = 16
    title_h = 24 if title else 0
    chart_h = len(rows) * (BAR_HEIGHT + BAR_GAP)
    width = 120 + CHART_WIDTH + 80
    height = title_h + chart_h + pad * 2

    bars = []
    if title:
        bars.append(f'<text x="{pad}" y="{pad + 12}" font-size="14" font-weight="bold" fill="#222">{title}</text>')
    for i, row in enumerate(rows):
        y = pad + title_h + i * (BAR_HEIGHT + BAR_GAP)
        bar_width = max(row[metric] / max_value * CHART_WIDTH, 2) if max_value else 2
        color = COLORS.get(row["language"], DEFAULT_COLOR)
        label = f"{format(row[metric], fmt)}{unit}"
        bars.append(
            f'<rect x="{pad + 120}" y="{y}" width="{bar_width:.1f}" height="{BAR_HEIGHT}" fill="{color}" />'
            f'<text x="{pad + 110}" y="{y + BAR_HEIGHT / 2 + 5}" text-anchor="end" font-size="13">{row["language"]}</text>'
            f'<text x="{pad + 120 + bar_width + 6:.1f}" y="{y + BAR_HEIGHT / 2 + 5}" font-size="12" fill="#555">{label}</text>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width + pad * 2}" height="{height}">'
        f'<rect width="100%" height="100%" fill="white" stroke="#ddd" />'
        f"{''.join(bars)}</svg>"
    )


def render_summary_table(entry: dict) -> str:
    rows = sorted(entry["results"], key=lambda r: r["min"])
    if not rows:
        return "<p><em>no data</em></p>"
    baseline = rows[0]

    lines = [
        '<table class="summary">',
        "<tr><th>Language</th><th>min (s)</th><th>median (s)</th><th>mean &plusmn; stdev (s)</th>"
        "<th>throughput (size/s)</th><th>peak RSS (MB)</th><th>speedup (vs fastest)</th></tr>",
    ]
    for row in rows:
        rs = stats.run_stats(row)
        spd = stats.speedup(row, baseline)
        thr = stats.throughput(row, entry["size"])
        cv = rs["stdev"] / rs["mean"] if rs["mean"] else 0.0
        noisy = " <em>(noisy)</em>" if cv > NOISY_CV_THRESHOLD else ""
        rss = f'{row["peak_rss_mb"]:.1f}' if row.get("peak_rss_mb") is not None else "n/a"
        spd_str = f"{spd:.2f}x" if spd is not None else "n/a"
        thr_str = f"{thr:,.0f}" if thr is not None else "n/a"
        lines.append(
            f'<tr><td>{row["language"]}</td><td>{row["min"]:.4f}</td><td>{row["median"]:.4f}</td>'
            f'<td>{rs["mean"]:.4f} &plusmn; {rs["stdev"]:.4f}{noisy}</td><td>{thr_str}</td>'
            f'<td>{rss}</td><td>{spd_str}</td></tr>'
        )
    lines.append("</table>")
    return "\n".join(lines)


def leaderboard_scores(data: list[dict]) -> list[tuple[str, float, int]]:
    """[(language, geomean speedup vs fastest, benchmarks scored), ...] sorted descending by score.

    Benchmarks whose cross-language outputs failed verification (entry["verified"]
    is False, e.g. an OUTPUT MISMATCH or an explicit skip policy) are excluded --
    an unverified result cannot win the leaderboard.
    """
    lang_ratios: dict[str, list[float]] = defaultdict(list)
    for entry in data:
        if entry.get("verified") is False:
            continue
        rows = [r for r in entry["results"] if r.get("min") is not None]
        if not rows:
            continue
        baseline = min(rows, key=lambda r: r["min"])
        for row in rows:
            spd = stats.speedup(row, baseline)
            if spd is not None:
                lang_ratios[row["language"]].append(spd)

    return sorted(
        ((language, stats.geomean_speedup(ratios), len(ratios)) for language, ratios in lang_ratios.items()),
        key=lambda x: x[1],
        reverse=True,
    )


def render_leaderboard(data: list[dict]) -> str:
    scored = leaderboard_scores(data)
    if not scored:
        return ""

    lines = [
        "<h2>Leaderboard</h2>",
        '<table class="summary">',
        "<tr><th>Language</th><th>geomean speedup (vs fastest)</th><th>benchmarks scored</th></tr>",
    ]
    for language, score, n in scored:
        lines.append(f"<tr><td>{language}</td><td>{score:.2f}x</td><td>{n}</td></tr>")
    lines.append("</table>")
    return "\n".join(lines)


def render_leaderboard_svg(data: list[dict], title: str = "") -> str:
    scored = leaderboard_scores(data)
    if not scored:
        return "<p><em>no data</em></p>"
    max_score = max(score for _, score, _ in scored)
    pad = 16
    title_h = 24 if title else 0
    chart_h = len(scored) * (BAR_HEIGHT + BAR_GAP)
    width = 120 + CHART_WIDTH + 80
    height = title_h + chart_h + pad * 2

    bars = []
    if title:
        bars.append(f'<text x="{pad}" y="{pad + 12}" font-size="14" font-weight="bold" fill="#222">{title}</text>')
    for i, (language, score, n) in enumerate(scored):
        y = pad + title_h + i * (BAR_HEIGHT + BAR_GAP)
        bar_width = max(score / max_score * CHART_WIDTH, 2) if max_score else 2
        color = COLORS.get(language, DEFAULT_COLOR)
        label = f"{score:.2f}x ({n})"
        bars.append(
            f'<rect x="{pad + 120}" y="{y}" width="{bar_width:.1f}" height="{BAR_HEIGHT}" fill="{color}" />'
            f'<text x="{pad + 110}" y="{y + BAR_HEIGHT / 2 + 5}" text-anchor="end" font-size="13">{language}</text>'
            f'<text x="{pad + 120 + bar_width + 6:.1f}" y="{y + BAR_HEIGHT / 2 + 5}" font-size="12" fill="#555">{label}</text>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width + pad * 2}" height="{height}">'
        f'<rect width="100%" height="100%" fill="white" stroke="#ddd" />'
        f"{''.join(bars)}</svg>"
    )


def render_verify_note(entry: dict) -> str:
    if "verified" not in entry:
        return ""
    if entry["verified"]:
        return ""
    reason = entry.get("verify_reason", "unknown reason")
    if reason.startswith("skipped:"):
        return f'<p class="verify-note">⚠ output verification skipped — {reason[len("skipped:"):].strip()}</p>'
    outputs = "; ".join(f"{lang}={value}" for lang, value in sorted(entry.get("_verify_outputs", {}).items()))
    detail = f" ({outputs})" if outputs else ""
    return f'<p class="verify-note mismatch">⚠ OUTPUT MISMATCH — {reason}{detail} — excluded from leaderboard</p>'


def render_html(data: list[dict]) -> str:
    sections = []
    for entry in data:
        sections.append(
            f'<h2>{entry["benchmark"]} <small>(size={entry["size"]})</small></h2>\n'
            f'{render_verify_note(entry)}\n'
            f'{render_summary_table(entry)}\n'
            f'<h3>time</h3>\n{render_chart(entry, "min", ".4f", "s")}\n'
            f'<h3>peak RSS</h3>\n{render_chart(entry, "peak_rss_mb", ".1f", "MB")}'
        )
    body = "\n".join(sections)
    leaderboard = render_leaderboard(data)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Benchmark results</title>
<style>
body {{ font-family: sans-serif; max-width: 800px; margin: 2rem auto; }}
h2 {{ margin-top: 2.5rem; }}
small {{ color: #888; font-weight: normal; }}
table.summary {{ border-collapse: collapse; margin: 0.5rem 0 1.5rem; font-size: 13px; }}
table.summary th, table.summary td {{ padding: 4px 10px; border: 1px solid #ddd; }}
table.summary td:not(:first-child) {{ text-align: right; }}
table.summary em {{ color: #b8860b; font-style: normal; }}
.verify-note {{ color: #b8860b; font-size: 13px; }}
.verify-note.mismatch {{ color: #c0392b; font-weight: bold; }}
</style>
</head>
<body>
<h1>Benchmark results</h1>
{leaderboard}
{body}
</body>
</html>
"""


def export_svgs(data: list[dict], export_dir: Path) -> None:
    export_dir.mkdir(parents=True, exist_ok=True)

    lb_path = export_dir / "leaderboard.svg"
    lb_path.write_text(render_leaderboard_svg(data, title="Leaderboard — geomean speedup vs fastest"))
    print(f"Wrote {lb_path}")

    for entry in data:
        bench = entry["benchmark"]
        time_path = export_dir / f"{bench}-time.svg"
        time_path.write_text(render_chart(entry, "min", ".4f", "s", title=f"{bench} — time (size={entry['size']})"))
        print(f"Wrote {time_path}")

        rss_path = export_dir / f"{bench}-rss.svg"
        rss_path.write_text(render_chart(entry, "peak_rss_mb", ".1f", "MB", title=f"{bench} — peak RSS (size={entry['size']})"))
        print(f"Wrote {rss_path}")


def export_csv(data: list[dict], path: Path) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["benchmark", "size", "language", "min", "median", "mean", "stdev",
             "throughput_per_sec", "peak_rss_mb", "speedup_vs_fastest"]
        )
        for entry in data:
            rows = sorted(entry["results"], key=lambda r: r["min"])
            if not rows:
                continue
            baseline = rows[0]
            for row in rows:
                rs = stats.run_stats(row)
                spd = stats.speedup(row, baseline)
                thr = stats.throughput(row, entry["size"])
                writer.writerow([
                    entry["benchmark"],
                    entry["size"],
                    row["language"],
                    f'{row["min"]:.6f}',
                    f'{row["median"]:.6f}',
                    f'{rs["mean"]:.6f}',
                    f'{rs["stdev"]:.6f}',
                    f"{thr:.4f}" if thr is not None else "",
                    row["peak_rss_mb"] if row.get("peak_rss_mb") is not None else "",
                    f"{spd:.4f}" if spd is not None else "",
                ])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_file", nargs="?", default=None)
    parser.add_argument("-o", "--output", default="report.html")
    parser.add_argument("--export-dir", default=None, help="write standalone <benchmark>-time.svg / -rss.svg files here instead of an HTML report")
    parser.add_argument("--csv", default=None, help="write a flat CSV of every benchmark/language stat to this path instead of an HTML report")
    args = parser.parse_args()

    path = Path(args.results_file).resolve() if args.results_file else latest_results_file()
    data = json.loads(path.read_text())

    if args.export_dir:
        export_svgs(data, Path(args.export_dir))
        return

    if args.csv:
        export_csv(data, Path(args.csv))
        print(f"Wrote {Path(args.csv).resolve()} from {path}")
        return

    out_path = ROOT / args.output
    out_path.write_text(render_html(data))
    print(f"Wrote {out_path.resolve()} from {path}")


if __name__ == "__main__":
    main()
