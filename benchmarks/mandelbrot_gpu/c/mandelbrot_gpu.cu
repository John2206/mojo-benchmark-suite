#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime.h>

#define MAX_ITER 1000
#define BLOCK 16

__global__ void mandelbrot_kernel(int *output, int n) {
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    if (row >= n || col >= n) return;

    double ci = -1.5 + 3.0 * row / n;
    double cr = -2.0 + 3.0 * col / n;
    double zr = 0.0, zi = 0.0;
    int iters = 0;
    while (iters < MAX_ITER) {
        double zr2 = zr * zr, zi2 = zi * zi;
        if (zr2 + zi2 > 4.0) break;
        double new_zi = 2.0 * zr * zi + ci;
        zr = zr2 - zi2 + cr;
        zi = new_zi;
        iters++;
    }
    output[row * n + col] = iters;
}

static int escape_iters_host(double cr, double ci) {
    double zr = 0.0, zi = 0.0;
    int i;
    for (i = 0; i < MAX_ITER; i++) {
        double zr2 = zr * zr, zi2 = zi * zi;
        if (zr2 + zi2 > 4.0) break;
        double new_zi = 2.0 * zr * zi + ci;
        zr = zr2 - zi2 + cr;
        zi = new_zi;
    }
    return i;
}

#define CUDA_CHECK(call) do { \
    cudaError_t err = (call); \
    if (err != cudaSuccess) { \
        fprintf(stderr, "CUDA error: %s\n", cudaGetErrorString(err)); \
        return 1; \
    } \
} while (0)

int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 4096;

    if (escape_iters_host(0.0, 0.0) != MAX_ITER) {
        fprintf(stderr, "self-check failed: origin should never escape\n");
        return 1;
    }
    if (escape_iters_host(2.0, 2.0) >= MAX_ITER) {
        fprintf(stderr, "self-check failed: far point should escape quickly\n");
        return 1;
    }

    int *d_output;
    size_t bytes = (size_t)n * n * sizeof(int);
    CUDA_CHECK(cudaMalloc(&d_output, bytes));

    dim3 block(BLOCK, BLOCK);
    dim3 grid((n + BLOCK - 1) / BLOCK, (n + BLOCK - 1) / BLOCK);
    mandelbrot_kernel<<<grid, block>>>(d_output, n);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaDeviceSynchronize());

    int *h_output = (int *)malloc(bytes);
    CUDA_CHECK(cudaMemcpy(h_output, d_output, bytes, cudaMemcpyDeviceToHost));

    long count = 0;
    for (long i = 0; i < (long)n * n; i++)
        if (h_output[i] == MAX_ITER) count++;

    printf("%ld\n", count);

    free(h_output);
    cudaFree(d_output);
    return 0;
}
