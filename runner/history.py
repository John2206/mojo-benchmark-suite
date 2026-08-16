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

    # points[benchmark][language] = [(timestamp, size, min_time), ...]
    points = defaultdict(lambda: defaultdict(list))
    for timestamp, data in runs:
        for entry in data:
            bench_key = entry["benchmark"]
            if args.benchmark and bench_key != args.benchmark:
                continue
            for row in entry["results"]:
                points[bench_key][row["language"]].append((timestamp, entry["size"], row["min"]))

    for bench_key in sorted(points):
        print(f"\n=== {bench_key} ===")
        for language in sorted(points[bench_key]):
            print(f"  {language}:")
            history = points[bench_key][language]
            prev_size = prev_time = None
            for timestamp, size, min_time in history:
                delta = ""
                if prev_size == size and prev_time:
                    pct = (min_time - prev_time) / prev_time * 100
                    delta = f"  ({pct:+.1f}%)"
                print(f"    {timestamp}  size={size:<10} {min_time:.4f}s{delta}")
                prev_size, prev_time = size, min_time


if __name__ == "__main__":
    main()
