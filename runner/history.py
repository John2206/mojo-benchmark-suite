#!/usr/bin/env python3
"""Shows how each language's time for each benchmark has changed across
past `--json` runs (results/*.json).

Usage:
    python3 runner/history.py [--benchmark fib]
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict

from languages import BENCHMARKS, ROOT

RESULTS_DIR = ROOT / "results"


def load_runs() -> list[tuple[str, dict]]:
    runs = []
    for path in sorted(RESULTS_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        runs.append((path.stem, data))
    return runs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", choices=list(BENCHMARKS), default=None)
    args = parser.parse_args()

    runs = load_runs()
    if not runs:
        print("No results/*.json files yet — run with --json first.")
        return

    # points[benchmark][language] = [(timestamp, size, min_time, peak_rss_mb), ...]
    # peak_rss_mb is None for runs recorded before memory tracking was added.
    points = defaultdict(lambda: defaultdict(list))
    for timestamp, data in runs:
        for entry in data:
            bench_key = entry["benchmark"]
            if args.benchmark and bench_key != args.benchmark:
                continue
            for row in entry["results"]:
                points[bench_key][row["language"]].append(
                    (timestamp, entry["size"], row["min"], row.get("peak_rss_mb"))
                )

    for bench_key in sorted(points):
        print(f"\n=== {bench_key} ===")
        for language in sorted(points[bench_key]):
            print(f"  {language}:")
            history = points[bench_key][language]
            prev_size = prev_time = prev_rss = None
            for timestamp, size, min_time, peak_rss_mb in history:
                time_delta = rss_delta = ""
                if prev_size == size and prev_time:
                    pct = (min_time - prev_time) / prev_time * 100
                    time_delta = f" ({pct:+.1f}%)"
                if prev_size == size and prev_rss and peak_rss_mb is not None:
                    pct = (peak_rss_mb - prev_rss) / prev_rss * 100
                    rss_delta = f" ({pct:+.1f}%)"
                rss_str = f"{peak_rss_mb:.1f}MB{rss_delta}" if peak_rss_mb is not None else "n/a"
                print(f"    {timestamp}  size={size:<10} time={min_time:.4f}s{time_delta}  RSS={rss_str}")
                prev_size, prev_time, prev_rss = size, min_time, peak_rss_mb


if __name__ == "__main__":
    main()
