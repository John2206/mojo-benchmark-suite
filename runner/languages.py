"""Per-language build/run command definitions for the benchmark runner."""
from __future__ import annotations

import shlex
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
PIXI = shutil.which("pixi") or str(Path.home() / ".pixi" / "bin" / "pixi")
RUSTC = shutil.which("rustc") or str(Path.home() / ".cargo" / "bin" / "rustc")

# mandelbrot_gpu, matmul_gpu, matmul_gpu_warm, and noop_gpu need real
# nvcc-compiled kernels for C/Rust/Java (Mojo and Python don't -- MAX compiles
# its own kernels, cupy.RawKernel JITs via NVRTC).
GPU_BENCHMARKS = {"mandelbrot_gpu", "matmul_gpu", "matmul_gpu_warm", "noop_gpu"}


@dataclass
class Language:
    name: str
    src_filename: Callable[[str], str]           # stem -> source filename
    build: Callable[[Path, Path, str], list] | None  # (src, bin_dir, stem) -> argv, or None
    run: Callable[[Path, Path, str, list], list]      # (src, bin_dir, stem, args) -> argv


def _java_class(stem: str) -> str:
    return stem.capitalize()


def _c_src_filename(stem: str) -> str:
    return f"{stem}.cu" if stem in GPU_BENCHMARKS else f"{stem}.c"


def _c_build(src: Path, bin_dir: Path, stem: str) -> list:
    if stem in GPU_BENCHMARKS:
        return ["nvcc", "-O3", "-arch=native", "-o", str(bin_dir / stem), str(src), "-lm"]
    return ["gcc", "-O2", "-o", str(bin_dir / stem), str(src), "-lm", "-lpthread"]


def _rust_build(src: Path, bin_dir: Path, stem: str) -> list:
    if stem == "noop_gpu":
        # No kernel to launch -- just Driver API init/alloc/free -- so there's
        # no *_kernel.cu to compile to PTX, unlike the other GPU benchmarks.
        return [RUSTC, "-O", "-o", str(bin_dir / stem), str(src), "-l", "cuda"]
    if stem in GPU_BENCHMARKS:
        kernel_src = src.with_name(f"{stem}_kernel.cu")
        ptx = bin_dir / f"{stem}.ptx"
        exe = bin_dir / stem
        cmd = (
            f"nvcc -ptx -arch=native {shlex.quote(str(kernel_src))} -o {shlex.quote(str(ptx))} "
            f"&& {shlex.quote(RUSTC)} -O -o {shlex.quote(str(exe))} {shlex.quote(str(src))} -l cuda"
        )
        return ["bash", "-c", cmd]
    return [RUSTC, "-O", "-o", str(bin_dir / stem), str(src)]


def _java_build(src: Path, bin_dir: Path, stem: str) -> list:
    if stem in GPU_BENCHMARKS:
        javac_path = shutil.which("javac")
        java_include = Path(javac_path).resolve().parent.parent / "include"
        shim_src = src.with_name(f"{_java_class(stem)}Gpu.cu")
        so_path = bin_dir / f"lib{stem}.so"
        cmd = (
            f"nvcc -O3 -arch=native -shared -Xcompiler -fPIC "
            f"-I {shlex.quote(str(java_include))} -I {shlex.quote(str(java_include / 'linux'))} "
            f"-o {shlex.quote(str(so_path))} {shlex.quote(str(shim_src))} "
            f"&& javac {shlex.quote(str(src))} -d {shlex.quote(str(bin_dir))}"
        )
        return ["bash", "-c", cmd]
    return ["javac", "--add-modules", "jdk.incubator.vector", str(src), "-d", str(bin_dir)]


def _java_run(src: Path, bin_dir: Path, stem: str, args: list) -> list:
    if stem in GPU_BENCHMARKS:
        return ["java", f"-Djava.library.path={bin_dir}", "-cp", str(bin_dir), _java_class(stem), *args]
    return ["java", "--add-modules", "jdk.incubator.vector", "-cp", str(bin_dir), _java_class(stem), *args]


LANGUAGES = {
    "c": Language(
        name="C",
        src_filename=_c_src_filename,
        build=_c_build,
        run=lambda src, bin_dir, stem, args: [str(bin_dir / stem), *args],
    ),
    "rust": Language(
        name="Rust",
        src_filename=lambda stem: f"{stem}.rs",
        build=_rust_build,
        run=lambda src, bin_dir, stem, args: [str(bin_dir / stem), *args],
    ),
    "java": Language(
        name="Java",
        src_filename=lambda stem: f"{_java_class(stem)}.java",
        build=_java_build,
        run=_java_run,
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
    "matmul": {"folder": "matmul", "stem": "matmul", "default_size": 400, "verify": {"rel_tol": 1e-6}},
    "mandelbrot": {"folder": "mandelbrot", "stem": "mandelbrot", "default_size": 800, "verify": {"skip": "escape-time iteration counts at boundary pixels are sensitive to tiny floating-point differences in Mojo's codegen vs C/Rust/Java/Python's (observed: 107581 vs Mojo's 107582 out of 640000 pixels at size=800, 1 pixel / 0.0009%) -- not a meaningful cross-language comparison"}},
    "nbody": {"folder": "nbody", "stem": "nbody", "default_size": 300, "verify": {"rel_tol": 1e-6}},
    "wordcount": {"folder": "wordcount", "stem": "wordcount", "default_size": 2_000_000},
    "mandelbrot_simd": {"folder": "mandelbrot_simd", "stem": "mandelbrot_simd", "default_size": 800, "verify": {"skip": "same escape-time boundary-pixel sensitivity as mandelbrot (observed: 107581 vs Mojo's 107582 out of 640000 pixels at size=800, 1 pixel / 0.0009%) -- not a meaningful cross-language comparison"}},
    "primes_parallel": {"folder": "primes_parallel", "stem": "primes_parallel", "default_size": 2_000_000},
    "ipvalidate": {"folder": "ipvalidate", "stem": "ipvalidate", "default_size": 2_000_000},
    "allocchurn": {"folder": "allocchurn", "stem": "allocchurn", "default_size": 5_000_000},
    "graph_bfs": {"folder": "graph_bfs", "stem": "graph_bfs", "default_size": 500_000},
    "bst": {"folder": "bst", "stem": "bst", "default_size": 300_000},
    "json_roundtrip": {"folder": "json_roundtrip", "stem": "json_roundtrip", "default_size": 200_000},
    "mandelbrot_gpu": {"folder": "mandelbrot_gpu", "stem": "mandelbrot_gpu", "default_size": 4096, "baseline": "noop_gpu", "verify": {"skip": "escape-time iteration counts at boundary pixels are sensitive to tiny floating-point differences between Mojo's TileTensor GPU codegen and raw CUDA C double arithmetic (observed: 44089 vs Mojo's 44085 out of ~262k boundary-adjacent pixels at size=512, ~0.01% of the total count) -- not a meaningful cross-language comparison"}},
    "matmul_gpu": {"folder": "matmul_gpu", "stem": "matmul_gpu", "default_size": 2048, "verify": {"rel_tol": 1e-6}, "baseline": "noop_gpu"},
    "matmul_gpu_warm": {"folder": "matmul_gpu_warm", "stem": "matmul_gpu_warm", "default_size": 500, "verify": {"rel_tol": 1e-6}, "baseline": "noop_gpu"},
    "crc32": {"folder": "crc32", "stem": "crc32", "default_size": 50_000_000},
    "base64": {"folder": "base64", "stem": "base64", "default_size": 20_000_000},
    "sha256": {"folder": "sha256", "stem": "sha256", "default_size": 2_000_000},
    "levenshtein": {"folder": "levenshtein", "stem": "levenshtein", "default_size": 5_000},
    "lru_cache": {"folder": "lru_cache", "stem": "lru_cache", "default_size": 2_000_000},
    "dijkstra": {"folder": "dijkstra", "stem": "dijkstra", "default_size": 300_000},
    "matmul_blocked": {"folder": "matmul_blocked", "stem": "matmul_blocked", "default_size": 600, "verify": {"rel_tol": 1e-6}},
    "lz77": {"folder": "lz77", "stem": "lz77", "default_size": 5_000_000},
    "montecarlo": {"folder": "montecarlo", "stem": "montecarlo", "default_size": 50_000_000, "verify": {"rel_tol": 1e-3}},
    "fft": {"folder": "fft", "stem": "fft", "default_size": 1_048_576, "verify": {"skip": "each language's floating-point reconstruction error converges to its own tiny value (~1e-10 to 1e-11) due to differing associativity — not a meaningful cross-language comparison"}},
    "noop": {"folder": "noop", "stem": "noop", "default_size": 0},
    "noop_gpu": {"folder": "noop_gpu", "stem": "noop_gpu", "default_size": 0},
}
