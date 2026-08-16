#!/usr/bin/env python3
"""Builds and times each language's implementation of each benchmark.

Usage:
    python3 runner/run.py [--benchmark fib|sort|matmul|all] [--size N]
                           [--repeats N] [--json]
"""
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from languages import BENCHMARKS, LANGUAGES, ROOT

BENCH_DIR = ROOT / "benchmarks"
BIN_DIR = ROOT / "bin"
RESULTS_DIR = ROOT / "results"


def build(lang_key: str, bench_key: str) -> tuple[Path, Path, str] | None:
    lang = LANGUAGES[lang_key]
    info = BENCHMARKS[bench_key]
    stem = info["stem"]
    src = BENCH_DIR / info["folder"] / lang_key / lang.src_filename(stem)
    if not src.exists():
        return None

    bin_dir = BIN_DIR / bench_key / lang_key
    bin_dir.mkdir(parents=True, exist_ok=True)

    if lang.build is not None:
        cmd = lang.build(src, bin_dir, stem)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  [{lang.name}] BUILD FAILED: {result.stderr.strip()}")
            return None

    return src, bin_dir, stem


def run_timed(lang_key: str, built: tuple[Path, Path, str], size: int, repeats: int) -> list[float] | None:
    lang = LANGUAGES[lang_key]
    src, bin_dir, stem = built
    cmd = lang.run(src, bin_dir, stem, [str(size)])

    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.perf_counter() - start
        if result.returncode != 0:
            print(f"  [{lang.name}] RUN FAILED: {result.stderr.strip()}")
            return None
        times.append(elapsed)
    return times


def run_benchmark(bench_key: str, size: int, repeats: int) -> dict:
    info = BENCHMARKS[bench_key]
    print(f"\n=== {bench_key} (size={size}) ===")
    rows = []
    for lang_key, lang in LANGUAGES.items():
        built = build(lang_key, bench_key)
        if built is None:
            src = BENCH_DIR / info["folder"] / lang_key / lang.src_filename(info["stem"])
            if not src.exists():
                print(f"  [{lang.name}] skipped: no source yet ({src.relative_to(ROOT)})")
            continue
        times = run_timed(lang_key, built, size, repeats)
        if times is None:
            continue
        rows.append({
            "language": lang.name,
            "min": min(times),
            "median": statistics.median(times),
            "runs": times,
        })

    rows.sort(key=lambda r: r["min"])
    print(f"  {'Language':<10} {'min (s)':>10} {'median (s)':>12}")
    for row in rows:
        print(f"  {row['language']:<10} {row['min']:>10.4f} {row['median']:>12.4f}")

    return {"benchmark": bench_key, "size": size, "repeats": repeats, "results": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", choices=[*BENCHMARKS, "all"], default="all")
    parser.add_argument("--size", type=int, default=None, help="only valid with a single --benchmark")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="dump results to results/<timestamp>.json")
    args = parser.parse_args()

    if args.size is not None and args.benchmark == "all":
        parser.error("--size requires a specific --benchmark (sizes aren't comparable across benchmarks)")

    bench_keys = list(BENCHMARKS) if args.benchmark == "all" else [args.benchmark]
    all_results = []
    for bench_key in bench_keys:
        size = args.size if args.size is not None else BENCHMARKS[bench_key]["default_size"]
        all_results.append(run_benchmark(bench_key, size, args.repeats))

    if args.json:
        RESULTS_DIR.mkdir(exist_ok=True)
        out_path = RESULTS_DIR / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        out_path.write_text(json.dumps(all_results, indent=2))
        print(f"\nWrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
