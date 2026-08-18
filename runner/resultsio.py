"""Loads results/*.json in either format.

Legacy files (written before this module existed) are a bare list of
per-benchmark entries. Current files are {"env": {...}, "startup_s": {...},
"benchmarks": [...]}. load_results() normalizes both into (env, entries) so
callers don't need to know which format they got.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from languages import ROOT

RESULTS_DIR = ROOT / "results"


def load_results(path: Path) -> tuple[dict, list[dict]]:
    data = json.loads(Path(path).read_text())
    if isinstance(data, list):
        return {}, data
    return data.get("env", {}), data.get("benchmarks", [])


def load_sweep(path: Path) -> tuple[dict, dict, list[dict]]:
    """(env, startup_s, sweeps) from a `run.py --sweep --json` file, i.e.
    {"env": {...}, "startup_s": {...}, "sweeps": [{"benchmark": ..., "by_size": [...]}]}."""
    data = json.loads(Path(path).read_text())
    return data.get("env", {}), data.get("startup_s", {}), data.get("sweeps", [])


def latest_results_file() -> Path:
    files = sorted(p for p in RESULTS_DIR.glob("*.json") if not p.name.startswith("sweep-"))
    if not files:
        sys.exit("No results/*.json files found — run with --json first.")
    return files[-1]


def latest_sweep_file() -> Path:
    files = sorted(RESULTS_DIR.glob("sweep-*.json"))
    if not files:
        sys.exit("No results/sweep-*.json files found — run with --sweep --json first.")
    return files[-1]
