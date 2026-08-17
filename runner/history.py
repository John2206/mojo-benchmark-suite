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

import stats
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
    parser.add_argument(
        "--threshold", type=float, default=5.0,
        help="minimum %% worse than the previous run (same size) to flag as a regression (default: 5.0). "
             "For time this is a floor — the effective threshold also rises with that run's own measurement "
             "noise (stdev), so a noisy benchmark needs a bigger jump to trigger. RSS has no per-repeat "
             "samples, so it always uses this flat threshold.",
    )
    args = parser.parse_args()

    runs = load_runs()
    if not runs:
        print("No results/*.json files yet — run with --json first.")
        return

    # points[benchmark][language] = [(timestamp, size, min_time, peak_rss_mb, noise_floor_pct), ...]
    # peak_rss_mb is None for runs recorded before memory tracking was added.
    # noise_floor_pct is this run's own stdev-derived regression threshold floor.
    points = defaultdict(lambda: defaultdict(list))
    for timestamp, data in runs:
        for entry in data:
            bench_key = entry["benchmark"]
            if args.benchmark and bench_key != args.benchmark:
                continue
            for row in entry["results"]:
                points[bench_key][row["language"]].append(
                    (timestamp, entry["size"], row["min"], row.get("peak_rss_mb"), stats.noise_floor_pct(row))
                )

    regression_count = 0
    for bench_key in sorted(points):
        print(f"\n=== {bench_key} ===")
        for language in sorted(points[bench_key]):
            print(f"  {language}:")
            history = points[bench_key][language]
            prev_size = prev_time = prev_rss = None
            for timestamp, size, min_time, peak_rss_mb, noise_floor in history:
                time_delta = rss_delta = ""
                if prev_size == size and prev_time:
                    pct = stats.pct_change(min_time, prev_time)
                    time_delta = f" ({pct:+.1f}%)"
                    effective_threshold = max(args.threshold, noise_floor)
                    if stats.is_regression(min_time, prev_time, effective_threshold):
                        time_delta += " ⚠ REGRESSION"
                        regression_count += 1
                if prev_size == size and prev_rss and peak_rss_mb is not None:
                    pct = stats.pct_change(peak_rss_mb, prev_rss)
                    rss_delta = f" ({pct:+.1f}%)"
                    if stats.is_regression(peak_rss_mb, prev_rss, args.threshold):
                        rss_delta += " ⚠ REGRESSION"
                        regression_count += 1
                rss_str = f"{peak_rss_mb:.1f}MB{rss_delta}" if peak_rss_mb is not None else "n/a"
                print(f"    {timestamp}  size={size:<10} time={min_time:.4f}s{time_delta}  RSS={rss_str}")
                prev_size, prev_time, prev_rss = size, min_time, peak_rss_mb

    if regression_count:
        print(f"\n{regression_count} regression(s) found (threshold: {args.threshold:.1f}%)")
    else:
        print(f"\nNo regressions found (threshold: {args.threshold:.1f}%)")


if __name__ == "__main__":
    main()
