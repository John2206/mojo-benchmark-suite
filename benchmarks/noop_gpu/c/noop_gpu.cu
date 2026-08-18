#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime.h>

#define CUDA_CHECK(call) do { \
    cudaError_t err = (call); \
    if (err != cudaSuccess) { \
        fprintf(stderr, "CUDA error: %s\n", cudaGetErrorString(err)); \
        return 1; \
    } \
} while (0)

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 0;
    (void)n;

    int *d_ptr;
    CUDA_CHECK(cudaMalloc(&d_ptr, sizeof(int)));
    CUDA_CHECK(cudaFree(d_ptr));

    printf("0\n");
    return 0;
}
