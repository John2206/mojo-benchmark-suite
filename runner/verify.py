"""Cross-language output verification.

Every benchmark program prints exactly one canonical value to stdout. This
module compares that value across languages so a broken-but-fast
implementation can't silently win a benchmark by computing the wrong thing.

Policies (declared per benchmark in languages.BENCHMARKS["verify"]):
    "exact"                 - stripped stdout byte-identical across languages (default)
    {"rel_tol": 1e-9}       - parse as float, compare relative to the median
    {"skip": "<reason>"}    - explicitly unverifiable; reason is required and surfaced
"""
from __future__ import annotations

import statistics

DEFAULT_POLICY = "exact"


def check_outputs(entry: dict, policy=DEFAULT_POLICY) -> dict:
    """entry: {"results": [{"language": str, "output": str | None, ...}, ...]}.

    Returns {"verified": bool, "reason": str, "outputs": {lang: value}}.
    """
    outputs = {
        row["language"]: row["output"]
        for row in entry.get("results", [])
        if row.get("output") is not None
    }

    if isinstance(policy, dict) and "skip" in policy:
        return {"verified": False, "reason": f"skipped: {policy['skip']}", "outputs": outputs}

    if len(outputs) < 2:
        return {"verified": True, "reason": "fewer than 2 languages to compare", "outputs": outputs}

    if isinstance(policy, dict) and "rel_tol" in policy:
        return _check_rel_tol(outputs, policy["rel_tol"])

    return _check_exact(outputs)


def _check_exact(outputs: dict) -> dict:
    values = list(outputs.values())
    if all(v == values[0] for v in values):
        return {"verified": True, "reason": "exact match", "outputs": outputs}
    return {"verified": False, "reason": "outputs differ", "outputs": outputs}


def _check_rel_tol(outputs: dict, rel_tol: float) -> dict:
    """Splits each output on whitespace so multi-value lines (e.g. nbody's
    "px py pz") are compared field-by-field, each against its own median."""
    parsed: dict[str, list[float]] = {}
    n_fields = None
    for lang, value in outputs.items():
        fields = str(value).split()
        try:
            parsed[lang] = [float(f) for f in fields]
        except ValueError:
            return {
                "verified": False,
                "reason": f"{lang} output {value!r} is not a parseable float",
                "outputs": outputs,
            }
        if n_fields is None:
            n_fields = len(parsed[lang])
        elif len(parsed[lang]) != n_fields:
            return {
                "verified": False,
                "reason": f"{lang} output {value!r} has {len(parsed[lang])} fields, expected {n_fields}",
                "outputs": outputs,
            }

    for i in range(n_fields or 0):
        medians = statistics.median(parsed[lang][i] for lang in parsed)
        denom = abs(medians) if medians != 0 else 1.0
        for lang, values in parsed.items():
            if abs(values[i] - medians) / denom > rel_tol:
                return {
                    "verified": False,
                    "reason": f"{lang} field {i}={values[i]} outside rel_tol={rel_tol} of median={medians}",
                    "outputs": outputs,
                }
    return {"verified": True, "reason": f"within rel_tol={rel_tol} of median", "outputs": outputs}
