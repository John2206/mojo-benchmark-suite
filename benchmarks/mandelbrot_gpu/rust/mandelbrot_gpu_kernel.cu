extern "C" __global__
void mandelbrot_kernel(int *output, int n) {
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    if (row >= n || col >= n) return;

    double ci = -1.5 + 3.0 * row / n;
    double cr = -2.0 + 3.0 * col / n;
    double zr = 0.0, zi = 0.0;
    int iters = 0;
    while (iters < 1000) {
        double zr2 = zr * zr, zi2 = zi * zi;
        if (zr2 + zi2 > 4.0) break;
        double new_zi = 2.0 * zr * zi + ci;
        zr = zr2 - zi2 + cr;
        zi = new_zi;
        iters++;
    }
    output[row * n + col] = iters;
}
