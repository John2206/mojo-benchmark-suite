#!/usr/bin/env python3
"""Builds and times each language's implementation of each benchmark.

Usage:
    python3 runner/run.py [--benchmark fib|sort|matmul|all] [--size N]
                           [--repeats N] [--json]
"""
from __future__ import annotations

import argparse
import json
import platform
import re
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import verify
from languages import BENCHMARKS, LANGUAGES, PIXI, ROOT, RUSTC

BENCH_DIR = ROOT / "benchmarks"
BIN_DIR = ROOT / "bin"
RESULTS_DIR = ROOT / "results"


def _cmd_version(cmd: list) -> str | None:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        text = (result.stdout or result.stderr).strip().splitlines()
        return text[0] if text else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def capture_env() -> dict:
    """A fingerprint of the machine/toolchain this run happened on, so
    history.py can tell "the numbers changed" apart from "the compiler
    changed underneath the numbers"."""
    loadavg = None
    try:
        loadavg = Path("/proc/loadavg").read_text().split()[:3]
    except OSError:
        pass
    governor = None
    try:
        governor = Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor").read_text().strip()
    except OSError:
        pass
    git_sha = None
    try:
        git_sha = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip() or None
    except OSError:
        pass

    cpu_model = _cmd_version(["bash", "-c", "lscpu | grep 'Model name:' | sed 's/Model name:[[:space:]]*//'"])

    return {
        "cpu_model": cpu_model or platform.processor() or None,
        "nproc": _cmd_version(["nproc"]),
        "kernel": platform.release(),
        "cpu_governor": governor,
        "load_average": loadavg,
        "git_sha": git_sha,
        "gcc": _cmd_version(["gcc", "--version"]),
        "rustc": _cmd_version([RUSTC, "--version"]),
        "javac": _cmd_version(["javac", "--version"]),
        "python3": _cmd_version(["python3", "--version"]),
        "mojo": _cmd_version([PIXI, "run", "--manifest-path", str(ROOT / "pixi.toml"), "mojo", "--version"]),
    }

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


def size_ladder(bench_key: str) -> list[int]:
    """The size ladder for a --sweep run of this benchmark: an explicit
    per-benchmark "sizes" override if declared (e.g. fib, which is
    exponential so a linear/geometric ladder derived from default_size would
    either be trivial or explode), else a geometric ladder derived from
    default_size: [d//8, d//4, d//2, d]."""
    info = BENCHMARKS[bench_key]
    if "sizes" in info:
        return list(info["sizes"])
    d = info["default_size"]
    ladder = sorted({max(1, d // 8), max(1, d // 4), max(1, d // 2), d})
    return ladder


def run_sweep(bench_key: str, repeats: int, baselines: dict[str, dict[str, float]]) -> dict:
    """Runs one benchmark across its whole size ladder. Verification (phase 1)
    runs at *every* size -- a self-check or cross-language agreement that only
    holds at one size is exactly the bug class this is meant to catch."""
    baseline_key = BENCHMARKS[bench_key].get("baseline", "noop")
    by_size = []
    for size in size_ladder(bench_key):
        entry = run_benchmark(bench_key, size, repeats, baselines.get(baseline_key))
        by_size.append(entry)
    return {"benchmark": bench_key, "by_size": by_size}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", choices=[*BENCHMARKS, "all"], default="all")
    parser.add_argument("--size", type=int, default=None, help="only valid with a single --benchmark")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="dump results to results/<timestamp>.json")
    parser.add_argument("--no-baseline", action="store_true", help="skip the noop/noop_gpu startup baseline runs (no 'compute' column)")
    parser.add_argument("--sweep", action="store_true", help="run each benchmark across a size ladder instead of one size (see size_ladder())")
    args = parser.parse_args()

    if args.size is not None and args.benchmark == "all":
        parser.error("--size requires a specific --benchmark (sizes aren't comparable across benchmarks)")
    if args.sweep and args.size is not None:
        parser.error("--sweep derives its own size ladder; --size doesn't apply")

    if args.benchmark == "all":
        # noop/noop_gpu are startup-cost baselines, not benchmarks in their
        # own right -- they're covered by compute_startup_baselines() below,
        # not run again here.
        bench_keys = [k for k in BENCHMARKS if k not in ("noop", "noop_gpu")]
    else:
        bench_keys = [args.benchmark]

    baselines: dict[str, dict[str, float]] = {}
    if not args.no_baseline:
        baselines = compute_startup_baselines(bench_keys, args.repeats)

    if args.sweep:
        sweeps = [run_sweep(bench_key, args.repeats, baselines) for bench_key in bench_keys]
        if args.json:
            RESULTS_DIR.mkdir(exist_ok=True)
            out_path = RESULTS_DIR / f"sweep-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
            payload = {"env": capture_env(), "startup_s": baselines, "sweeps": sweeps}
            out_path.write_text(json.dumps(payload, indent=2))
            print(f"\nWrote {out_path.relative_to(ROOT)}")
        return

    all_results = []
    for bench_key in bench_keys:
        size = args.size if args.size is not None else BENCHMARKS[bench_key]["default_size"]
        baseline_key = BENCHMARKS[bench_key].get("baseline", "noop")
        all_results.append(run_benchmark(bench_key, size, args.repeats, baselines.get(baseline_key)))

    if args.json:
        RESULTS_DIR.mkdir(exist_ok=True)
        out_path = RESULTS_DIR / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        startup_s = {k: v for k, v in baselines.items()}
        payload = {"env": capture_env(), "startup_s": startup_s, "benchmarks": all_results}
        out_path.write_text(json.dumps(payload, indent=2))
        print(f"\nWrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
