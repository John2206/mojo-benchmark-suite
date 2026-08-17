"""Small stats helpers shared by report.py and history.py."""
from __future__ import annotations

import statistics


def run_stats(row: dict) -> dict:
    """mean/stdev from row['runs']; stdev is 0.0 (not an error) for repeats<2."""
    runs = row["runs"]
    return {
        "mean": statistics.mean(runs),
        "stdev": statistics.stdev(runs) if len(runs) > 1 else 0.0,
    }


def speedup(row: dict, baseline_row: dict | None, metric: str = "min") -> float | None:
    """baseline_time / row_time; 1.0 = as fast as baseline, <1.0 = slower."""
    if baseline_row is None or row[metric] == 0:
        return None
    return baseline_row[metric] / row[metric]


def geomean_speedup(ratios: list[float]) -> float | None:
    """Geometric mean of a list of per-benchmark speedup ratios; None if empty."""
    return statistics.geometric_mean(ratios) if ratios else None


def pct_change(new: float, old: float) -> float | None:
    return (new - old) / old * 100 if old else None


def is_regression(new: float, old: float, threshold_pct: float) -> bool:
    """True if new is more than threshold_pct% slower/larger than old."""
    delta = pct_change(new, old)
    return delta is not None and delta > threshold_pct


def noise_floor_pct(row: dict, multiplier: float = 2.0) -> float:
    """A regression threshold floor derived from this run's own noise: stdev
    as a %% of mean, scaled by multiplier. A noisy measurement needs a bigger
    jump before it's worth flagging as a real regression."""
    rs = run_stats(row)
    if not rs["mean"]:
        return 0.0
    return multiplier * (rs["stdev"] / rs["mean"] * 100)


def throughput(row: dict, size: float) -> float | None:
    """size / min time. What 'size' means is benchmark-specific (elements,
    grid cells, recursion depth, ...) — comparable across runs of the same
    benchmark, not across different benchmarks."""
    return size / row["min"] if row.get("min") else None
