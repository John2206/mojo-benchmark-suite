"""Empirical complexity fitting and crossover-bracket detection for scaling
sweeps (runner/run.py --sweep).

fit_complexity() does a least-squares fit of ln(time) vs ln(size) -- the
slope approximates the empirical exponent of an assumed power-law time(size)
~= size**slope, and R^2 says how much to trust that slope. A low R^2 means
"don't believe this exponent," not "here's a wrong number to quote."

find_crossovers() finds, for a pair of languages measured at the same size
ladder, the adjacent ladder points where the faster language flips -- no
interpolation, just the bracketing sizes either side of the flip.
"""
from __future__ import annotations

import math
from itertools import combinations


def fit_complexity(sizes: list[float], times: list[float]) -> dict:
    """Least-squares fit of ln(time) = slope * ln(size) + intercept.

    Returns {"slope": float, "r_squared": float, "n": int}, or
    {"slope": None, "r_squared": None, "n": n} if fewer than 2 usable
    (size, time) pairs (both must be positive to take a log).
    """
    pairs = [(s, t) for s, t in zip(sizes, times) if s and t and s > 0 and t > 0]
    if len(pairs) < 2:
        return {"slope": None, "r_squared": None, "n": len(pairs)}

    xs = [math.log(s) for s, _ in pairs]
    ys = [math.log(t) for _, t in pairs]
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n

    ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    ss_xx = sum((x - mean_x) ** 2 for x in xs)
    if ss_xx == 0:
        return {"slope": None, "r_squared": None, "n": n}

    slope = ss_xy / ss_xx
    intercept = mean_y - slope * mean_x

    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0

    return {"slope": slope, "r_squared": r_squared, "n": n}


def find_crossovers(sizes: list[float], times_a: list[float], times_b: list[float]) -> list[dict]:
    """Adjacent ladder points [size_i, size_{i+1}] where sign(t_a - t_b)
    flips between i and i+1. No interpolation -- the bracket itself is the
    answer, since we only have measurements at the ladder points.

    Returns a list of {"bracket": [size_i, size_{i+1}], "before": "a"|"b",
    "after": "a"|"b"} -- which language was faster before/after the flip.
    """
    pairs = [
        (s, a, b)
        for s, a, b in zip(sizes, times_a, times_b)
        if a is not None and b is not None
    ]
    pairs.sort(key=lambda p: p[0])

    crossovers = []
    for (s0, a0, b0), (s1, a1, b1) in zip(pairs, pairs[1:]):
        diff0 = a0 - b0
        diff1 = a1 - b1
        if diff0 == 0 or diff1 == 0:
            continue
        if (diff0 > 0) != (diff1 > 0):
            crossovers.append({
                "bracket": [s0, s1],
                "before": "a" if diff0 < 0 else "b",
                "after": "a" if diff1 < 0 else "b",
            })
    return crossovers


def all_crossovers(sizes: list[float], times_by_lang: dict[str, list[float]]) -> dict:
    """{(lang_a, lang_b): [crossover, ...], ...} for every language pair."""
    result = {}
    for lang_a, lang_b in combinations(sorted(times_by_lang), 2):
        crossings = find_crossovers(sizes, times_by_lang[lang_a], times_by_lang[lang_b])
        if crossings:
            result[(lang_a, lang_b)] = crossings
    return result
