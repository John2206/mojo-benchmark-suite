"""Per-language build/run command definitions for the benchmark runner."""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
PIXI = shutil.which("pixi") or str(Path.home() / ".pixi" / "bin" / "pixi")


@dataclass
class Language:
    name: str
    src_filename: Callable[[str], str]           # stem -> source filename
    build: Callable[[Path, Path, str], list] | None  # (src, bin_dir, stem) -> argv, or None
    run: Callable[[Path, Path, str, list], list]      # (src, bin_dir, stem, args) -> argv


def _java_class(stem: str) -> str:
    return stem.capitalize()


LANGUAGES = {
    "c": Language(
        name="C",
        src_filename=lambda stem: f"{stem}.c",
        build=lambda src, bin_dir, stem: ["gcc", "-O2", "-o", str(bin_dir / stem), str(src)],
        run=lambda src, bin_dir, stem, args: [str(bin_dir / stem), *args],
    ),
    "rust": Language(
        name="Rust",
        src_filename=lambda stem: f"{stem}.rs",
        build=lambda src, bin_dir, stem: ["rustc", "-O", "-o", str(bin_dir / stem), str(src)],
        run=lambda src, bin_dir, stem, args: [str(bin_dir / stem), *args],
    ),
    "java": Language(
        name="Java",
        src_filename=lambda stem: f"{_java_class(stem)}.java",
        build=lambda src, bin_dir, stem: ["javac", str(src), "-d", str(bin_dir)],
        run=lambda src, bin_dir, stem, args: ["java", "-cp", str(bin_dir), _java_class(stem), *args],
    ),
    "python": Language(
        name="Python",
        src_filename=lambda stem: f"{stem}.py",
        build=None,
        run=lambda src, bin_dir, stem, args: ["python3", str(src), *args],
    ),
    "mojo": Language(
        name="Mojo",
        src_filename=lambda stem: f"{stem}.mojo",
        build=lambda src, bin_dir, stem: [
            PIXI, "run", "--manifest-path", str(ROOT / "pixi.toml"),
            "mojo", "build", str(src), "-o", str(bin_dir / stem),
        ],
        run=lambda src, bin_dir, stem, args: [str(bin_dir / stem), *args],
    ),
}

BENCHMARKS = {
    "fib": {"folder": "fibonacci", "stem": "fib", "default_size": 32},
    "sort": {"folder": "sort", "stem": "sort", "default_size": 2_000_000},
    "matmul": {"folder": "matmul", "stem": "matmul", "default_size": 400},
}
