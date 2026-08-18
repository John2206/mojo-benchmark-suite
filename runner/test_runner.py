#!/usr/bin/env python3
"""Plain-assert tests for the runner modules. No framework — run directly:

    python3 runner/test_runner.py
"""
from __future__ import annotations

import json
import random
import tempfile
from pathlib import Path

import resultsio
import scaling
import verify


def _entry(**lang_outputs) -> dict:
    return {"results": [{"language": lang, "output": out} for lang, out in lang_outputs.items()]}


def test_verify_exact_agree():
    entry = _entry(C="42", Rust="42", Java="42", Python="42", Mojo="42")
    result = verify.check_outputs(entry, "exact")
    assert result["verified"] is True, result
    assert result["reason"] == "exact match"


def test_verify_exact_disagree():
    entry = _entry(C="42", Rust="42", Java="43", Python="42", Mojo="42")
    result = verify.check_outputs(entry, "exact")
    assert result["verified"] is False, result
    assert "differ" in result["reason"]


def test_verify_rel_tol_within():
    entry = _entry(C="3.14159012", Rust="3.14159034", Java="3.14159001", Python="3.14158999", Mojo="3.14159050")
    result = verify.check_outputs(entry, {"rel_tol": 1e-6})
    assert result["verified"] is True, result


def test_verify_rel_tol_multi_field():
    entry = _entry(
        C="0.000008 0.000015 0.000023",
        Rust="0.000008 0.000015 0.000023",
        Mojo="0.000008 0.000015 0.000023",
        Java="0.000008 0.000015 0.000023",
        Python="0.000008 0.000015 0.000023",
    )
    result = verify.check_outputs(entry, {"rel_tol": 1e-6})
    assert result["verified"] is True, result


def test_verify_rel_tol_outside():
    entry = _entry(C="3.14159012", Rust="3.20000000", Java="3.14159001", Python="3.14158999", Mojo="3.14159050")
    result = verify.check_outputs(entry, {"rel_tol": 1e-6})
    assert result["verified"] is False, result


def test_verify_skip_policy():
    entry = _entry(C="1e-10", Rust="2e-11", Java="3e-10", Python="1e-11", Mojo="5e-10")
    result = verify.check_outputs(entry, {"skip": "floating point associativity differs per language"})
    assert result["verified"] is False, result
    assert "skipped" in result["reason"]
    assert "floating point" in result["reason"]


def test_resultsio_legacy_bare_list():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "legacy.json"
        path.write_text(json.dumps([{"benchmark": "fib", "size": 32, "repeats": 5, "results": []}]))
        env, entries = resultsio.load_results(path)
        assert env == {}, env
        assert len(entries) == 1
        assert entries[0]["benchmark"] == "fib"


def test_resultsio_new_format():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "new.json"
        payload = {
            "env": {"gcc": "13.3.0"},
            "startup_s": {"noop": {"C": 0.001}},
            "benchmarks": [{"benchmark": "fib", "size": 32, "repeats": 5, "results": []}],
        }
        path.write_text(json.dumps(payload))
        env, entries = resultsio.load_results(path)
        assert env == {"gcc": "13.3.0"}, env
        assert len(entries) == 1
        assert entries[0]["benchmark"] == "fib"


def test_scaling_exact_quadratic():
    sizes = [10, 20, 40, 80, 160]
    times = [0.001 * (s ** 2) for s in sizes]
    fit = scaling.fit_complexity(sizes, times)
    assert abs(fit["slope"] - 2.0) < 0.01, fit
    assert fit["r_squared"] > 0.999, fit


def test_scaling_noisy_data():
    random.seed(0)
    sizes = [10, 20, 40, 80, 160]
    times = [0.001 * random.uniform(0.5, 50) for _ in sizes]
    fit = scaling.fit_complexity(sizes, times)
    assert fit["r_squared"] < 0.8, fit


def test_scaling_crossover_bracket():
    sizes = [10, 20, 40, 80, 160]
    times_a = [1, 2, 4, 8, 30]        # a: accelerating, overtakes b once
    times_b = [5, 6, 7, 9, 10]        # b: nearly flat
    crossings = scaling.find_crossovers(sizes, times_a, times_b)
    assert len(crossings) == 1, crossings
    assert crossings[0]["bracket"] == [80, 160], crossings


def main():
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_") and callable(obj)]
    failures = []
    for test in tests:
        try:
            test()
            print(f"  PASS {test.__name__}")
        except AssertionError as e:
            failures.append(test.__name__)
            print(f"  FAIL {test.__name__}: {e}")
    print(f"\n{len(tests) - len(failures)}/{len(tests)} passed")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
