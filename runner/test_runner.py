#!/usr/bin/env python3
"""Plain-assert tests for the runner modules. No framework — run directly:

    python3 runner/test_runner.py
"""
from __future__ import annotations

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
