import sys

import cupy as cp

N = 256

KERNEL_SRC = r"""
extern "C" __global__
void matmul_kernel(const double* a, const double* b, double* c, int n) {
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    if (row >= n || col >= n) return;

    double acc = 0.0;
    for (int k = 0; k < n; k++) {
        acc += a[row * n + k] * b[k * n + col];
    }
    c[row * n + col] = acc;
}
"""

matmul_kernel = cp.RawKernel(KERNEL_SRC, "matmul_kernel")


def main():
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    n = N

    i = cp.arange(n, dtype=cp.int64).reshape(n, 1)
    j = cp.arange(n, dtype=cp.int64).reshape(1, n)
    a = ((i * 3 + j) % 13).astype(cp.float64)
    b = ((i + j * 2) % 17).astype(cp.float64)
    c = cp.zeros((n, n), dtype=cp.float64)

    k = cp.arange(n, dtype=cp.int64)
    expected = float(cp.sum((k % 13).astype(cp.float64) * (k % 17).astype(cp.float64)))

    block = (16, 16)
    grid = ((n + block[0] - 1) // block[0], (n + block[1] - 1) // block[1])

    corner_n = 0.0
    for it in range(iterations):
        matmul_kernel(grid, block, (a, b, c, n))
        corner0 = float(c[0, 0])
        corner_n = float(c[n - 1, n - 1])
        if corner0 != expected:
            raise AssertionError(f"self-check failed at iteration {it}: c[0][0] mismatch")

    print(f"{corner_n:.2f}")


if __name__ == "__main__":
    main()
