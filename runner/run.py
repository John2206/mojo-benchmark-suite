#!/usr/bin/env python3
"""Builds and times each language's implementation of each benchmark.

Usage:
    python3 runner/run.py [--benchmark fib|sort|matmul|all] [--size N]
                           [--repeats N] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import verify
from languages import BENCHMARKS, LANGUAGES, ROOT

BENCH_DIR = ROOT / "benchmarks"
BIN_DIR = ROOT / "bin"
RESULTS_DIR = ROOT / "results"

MAX_RSS_RE = re.compile(r"Maximum resident set size \(kbytes\): (\d+)")


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


def run_timed(lang_key: str, built: tuple[Path, Path, str], size: int, repeats: int) -> tuple[list[float], list[int], list[str]] | None:
    lang = LANGUAGES[lang_key]
    src, bin_dir, stem = built
    cmd = ["/usr/bin/time", "-v", *lang.run(src, bin_dir, stem, [str(size)])]

    times = []
    peak_rss_kb = []
    stdouts = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.perf_counter() - start
        if result.returncode != 0:
            print(f"  [{lang.name}] RUN FAILED: {result.stderr.strip()}")
            return None
        match = MAX_RSS_RE.search(result.stderr)
        times.append(elapsed)
        peak_rss_kb.append(int(match.group(1)) if match else 0)
        stdouts.append(result.stdout.strip())
    return times, peak_rss_kb, stdouts


def run_benchmark(bench_key: str, size: int, repeats: int, startup_s: dict[str, float] | None = None) -> dict:
    info = BENCHMARKS[bench_key]
    startup_s = startup_s or {}
    print(f"\n=== {bench_key} (size={size}) ===")
    rows = []
    for lang_key, lang in LANGUAGES.items():
        built = build(lang_key, bench_key)
        if built is None:
            src = BENCH_DIR / info["folder"] / lang_key / lang.src_filename(info["stem"])
            if not src.exists():
                print(f"  [{lang.name}] skipped: no source yet ({src.relative_to(ROOT)})")
            continue
        timed = run_timed(lang_key, built, size, repeats)
        if timed is None:
            continue
        times, peak_rss_kb, stdouts = timed
        min_time = min(times)
        base = startup_s.get(lang.name)
        compute = (min_time - base) if base is not None and min_time > base else None
        rows.append({
            "language": lang.name,
            "min": min_time,
            "median": statistics.median(times),
            "runs": times,
            "peak_rss_mb": max(peak_rss_kb) / 1024,
            "output": stdouts[0] if stdouts else None,
            "output_stable": all(o == stdouts[0] for o in stdouts) if stdouts else True,
            "compute": compute,
        })

    rows.sort(key=lambda r: r["min"])
    print(f"  {'Language':<10} {'min (s)':>10} {'median (s)':>12} {'compute (s)':>12} {'peak RSS (MB)':>14}")
    for row in rows:
        compute_str = f"{row['compute']:.4f}" if row["compute"] is not None else "n/a"
        print(f"  {row['language']:<10} {row['min']:>10.4f} {row['median']:>12.4f} {compute_str:>12} {row['peak_rss_mb']:>14.1f}")

    policy = info.get("verify", "exact")
    verify_result = verify.check_outputs({"results": rows}, policy)
    if not verify_result["verified"] and not (isinstance(policy, dict) and "skip" in policy):
        print(f"  ⚠ OUTPUT MISMATCH: {verify_result['reason']}")
        for lang_name, value in verify_result["outputs"].items():
            print(f"    {lang_name}: {value}")
    unstable = [row["language"] for row in rows if not row.get("output_stable", True)]
    if unstable:
        print(f"  ⚠ non-deterministic output across repeats: {', '.join(unstable)}")

    return {
        "benchmark": bench_key,
        "size": size,
        "repeats": repeats,
        "results": rows,
        "verified": verify_result["verified"],
        "verify_reason": verify_result["reason"],
    }


def compute_startup_baselines(bench_keys: list[str], repeats: int) -> dict[str, dict[str, float]]:
    """Runs whichever of noop/noop_gpu the requested benchmarks need as their
    "baseline", and returns {baseline_key: {language_name: min_time_s}}.
    A benchmark's own wall-clock time minus this is its "compute" time --
    what the language does once its process/runtime is already up.
    """
    needed = {BENCHMARKS[k].get("baseline", "noop") for k in bench_keys if k not in ("noop", "noop_gpu")}
    baselines: dict[str, dict[str, float]] = {}
    for baseline_key in sorted(needed):
        print(f"\n--- computing startup baseline: {baseline_key} ---")
        entry = run_benchmark(baseline_key, BENCHMARKS[baseline_key]["default_size"], repeats)
        baselines[baseline_key] = {row["language"]: row["min"] for row in entry["results"]}
    return baselines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", choices=[*BENCHMARKS, "all"], default="all")
    parser.add_argument("--size", type=int, default=None, help="only valid with a single --benchmark")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="dump results to results/<timestamp>.json")
    parser.add_argument("--no-baseline", action="store_true", help="skip the noop/noop_gpu startup baseline runs (no 'compute' column)")
    args = parser.parse_args()

    if args.size is not None and args.benchmark == "all":
        parser.error("--size requires a specific --benchmark (sizes aren't comparable across benchmarks)")

    bench_keys = list(BENCHMARKS) if args.benchmark == "all" else [args.benchmark]

    baselines: dict[str, dict[str, float]] = {}
    if not args.no_baseline:
        baselines = compute_startup_baselines(bench_keys, args.repeats)

    all_results = []
    for bench_key in bench_keys:
        if bench_key in ("noop", "noop_gpu") and bench_key in baselines:
            # Already run as part of the baseline pass -- don't run it twice.
            continue
        size = args.size if args.size is not None else BENCHMARKS[bench_key]["default_size"]
        baseline_key = BENCHMARKS[bench_key].get("baseline", "noop")
        all_results.append(run_benchmark(bench_key, size, args.repeats, baselines.get(baseline_key)))

    if args.json:
        RESULTS_DIR.mkdir(exist_ok=True)
        out_path = RESULTS_DIR / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        startup_s = {k: v for k, v in baselines.items()}
        payload = {"env": {}, "startup_s": startup_s, "benchmarks": all_results}
        out_path.write_text(json.dumps(payload, indent=2))
        print(f"\nWrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
