#include <jni.h>
#include <cuda_runtime.h>
#include <stdlib.h>

#define BLOCK 16
#define N 256

__global__ void matmul_kernel(const double *a, const double *b, double *c, int n) {
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    if (row >= n || col >= n) return;

    double acc = 0.0;
    for (int k = 0; k < n; k++)
        acc += a[row * n + k] * b[k * n + col];
    c[row * n + col] = acc;
}

#define CUDA_CHECK(call) do { \
    cudaError_t err = (call); \
    if (err != cudaSuccess) { \
        jclass exc = env->FindClass("java/lang/RuntimeException"); \
        env->ThrowNew(exc, cudaGetErrorString(err)); \
        return 0; \
    } \
} while (0)

extern "C"
JNIEXPORT jdouble JNICALL Java_Matmul_1gpu_1warm_runKernel(JNIEnv *env, jclass cls, jint iterations) {
    int n = N;
    size_t bytes = (size_t)n * n * sizeof(double);

    double *h_a = (double *)malloc(bytes);
    double *h_b = (double *)malloc(bytes);
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            h_a[i * n + j] = (double)((i * 3 + j) % 13);
            h_b[i * n + j] = (double)((i + j * 2) % 17);
        }

    double expected = 0.0;
    for (int k = 0; k < n; k++)
        expected += h_a[k] * h_b[k * n];

    double *d_a, *d_b, *d_c;
    CUDA_CHECK(cudaMalloc(&d_a, bytes));
    CUDA_CHECK(cudaMalloc(&d_b, bytes));
    CUDA_CHECK(cudaMalloc(&d_c, bytes));
    CUDA_CHECK(cudaMemcpy(d_a, h_a, bytes, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_b, h_b, bytes, cudaMemcpyHostToDevice));

    dim3 block(BLOCK, BLOCK);
    dim3 grid((n + BLOCK - 1) / BLOCK, (n + BLOCK - 1) / BLOCK);

    double corner0 = 0.0, cornerN = 0.0;
    for (int it = 0; it < iterations; it++) {
        matmul_kernel<<<grid, block>>>(d_a, d_b, d_c, n);
        CUDA_CHECK(cudaGetLastError());
        CUDA_CHECK(cudaMemcpy(&corner0, d_c, sizeof(double), cudaMemcpyDeviceToHost));
        CUDA_CHECK(cudaMemcpy(&cornerN, d_c + (size_t)(n - 1) * n + (n - 1), sizeof(double), cudaMemcpyDeviceToHost));
        if (corner0 != expected) {
            jclass exc = env->FindClass("java/lang/RuntimeException");
            env->ThrowNew(exc, "self-check failed: c[0][0] mismatch");
            return 0;
        }
    }

    free(h_a);
    free(h_b);
    cudaFree(d_a);
    cudaFree(d_b);
    cudaFree(d_c);
    return cornerN;
}
