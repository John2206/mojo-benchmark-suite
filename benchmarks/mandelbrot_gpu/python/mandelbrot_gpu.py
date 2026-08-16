import sys

import cupy as cp

MAX_ITER = 1000

KERNEL_SRC = r"""
extern "C" __global__
void mandelbrot_kernel(int* output, int n) {{
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    if (row >= n || col >= n) return;

    double ci = -1.5 + 3.0 * row / n;
    double cr = -2.0 + 3.0 * col / n;
    double zr = 0.0, zi = 0.0;
    int iters = 0;
    while (iters < {max_iter}) {{
        double zr2 = zr * zr;
        double zi2 = zi * zi;
        if (zr2 + zi2 > 4.0) break;
        double new_zi = 2.0 * zr * zi + ci;
        zr = zr2 - zi2 + cr;
        zi = new_zi;
        iters++;
    }}
    output[row * n + col] = iters;
}}
""".format(max_iter=MAX_ITER)

mandelbrot_kernel = cp.RawKernel(KERNEL_SRC, "mandelbrot_kernel")


def escape_iters_single(cr, ci):
    zr = zi = 0.0
    i = 0
    while i < MAX_ITER:
        zr2, zi2 = zr * zr, zi * zi
        if zr2 + zi2 > 4.0:
            break
        zi = 2.0 * zr * zi + ci
        zr = zr2 - zi2 + cr
        i += 1
    return i


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4096

    assert escape_iters_single(0.0, 0.0) == MAX_ITER, "self-check failed: origin should never escape"
    assert escape_iters_single(2.0, 2.0) < MAX_ITER, "self-check failed: far point should escape quickly"

    output = cp.zeros((n, n), dtype=cp.int32)
    block = (16, 16)
    grid = ((n + block[0] - 1) // block[0], (n + block[1] - 1) // block[1])
    mandelbrot_kernel(grid, block, (output, n))
    cp.cuda.Stream.null.synchronize()

    count = int(cp.sum(output == MAX_ITER))
    print(count)


if __name__ == "__main__":
    main()
