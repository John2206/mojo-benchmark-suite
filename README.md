# mojo-benchmark-suite

Compares Mojo against Java, Python, C, and Rust on identical small
workloads:

- **fib** — recursive fibonacci, function-call overhead
- **sort** — builtin sort of random ints
- **matmul** — naive triple-loop matrix multiply
- **mandelbrot** — scalar per-pixel escape-time fractal (no explicit SIMD)
- **nbody** — O(n²) pairwise gravity simulation, momentum-conserving
- **wordcount** — hash map insert/increment over a small fixed vocabulary
  (C uses a hand-rolled open-addressing table — C has no stdlib hash map)
- **mandelbrot_simd** — Mojo only. Same fractal, but 4 pixels at a time using
  Mojo's native `SIMD` type with lane masking, ~20% faster than scalar Mojo
  and edges out scalar C/Rust too. The other languages don't have a stdlib
  path to this (C needs AVX intrinsics, Rust needs nightly `portable_simd`
  or `unsafe` arch intrinsics, Java needs the incubator Vector API, Python
  would need numpy) — the runner just reports them as skipped.
- **primes_parallel** — C/Rust/Java/Python only. Counts primes below N with
  4 worker threads/processes (C `pthread`, Rust `std::thread`, Java
  `Thread`, **Python `multiprocessing`** since threads are GIL-bound for
  CPU work). No Mojo entry: current stable Mojo has no OS-thread API, only
  an experimental async `TaskGroup` the mojo-syntax skill says isn't ready
  to use yet.
- **ipvalidate** — hand-rolled dotted-quad string validator (no regex
  anywhere, including Mojo which has none in stdlib), exercises each
  language's raw string/char handling.
- **allocchurn** — many small alloc/use/free cycles; shows allocator and GC
  overhead (see peak RSS below — Java's heap balloons here).

## Setup

- C: `gcc` (already on most systems)
- Rust: [rustup](https://rustup.rs)
- Java: JDK (`javac`/`java`)
- Python: `python3`
- Mojo: [pixi](https://pixi.prefix.dev), then `pixi add mojo` (already
  configured in `pixi.toml`)

## Usage

```sh
python3 runner/run.py                       # run all benchmarks, default sizes
python3 runner/run.py --benchmark fib        # just one benchmark
python3 runner/run.py --benchmark sort --size 5000000
python3 runner/run.py --repeats 10 --json    # more samples, dump results/<timestamp>.json
```

Each benchmark program self-checks its own output (e.g. sort verifies the
array is sorted, matmul spot-checks a cell) and exits non-zero on failure —
the runner reports that language as failed rather than printing a bogus time.

Every run also captures peak RSS via `/usr/bin/time -v` alongside wall time,
shown as a "peak RSS (MB)" column and saved in the JSON output.

```sh
python3 runner/history.py                   # trend across all past --json runs
python3 runner/history.py --benchmark sort   # just one benchmark
python3 runner/report.py                     # HTML bar-chart report from the latest run
python3 runner/report.py results/foo.json -o out.html
```

## Timing methodology

Timing wraps the whole process (`subprocess` + `time.perf_counter`), not an
in-program timer. This is a deliberate simplification: it's simple, fair
across compiled and interpreted languages, and it captures real startup cost
(e.g. JVM/interpreter startup). It does *not* isolate steady-state/JIT-warmed
performance — take these numbers as "run this program end to end", not as a
microarchitectural comparison.
