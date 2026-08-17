extern "C" __global__
void matmul_kernel(const double *a, const double *b, double *c, int n) {
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    if (row >= n || col >= n) return;

    double acc = 0.0;
    for (int k = 0; k < n; k++)
        acc += a[row * n + k] * b[k * n + col];
    c[row * n + col] = acc;
}
