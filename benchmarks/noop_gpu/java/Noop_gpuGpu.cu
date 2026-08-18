#include <jni.h>
#include <cuda_runtime.h>

#define CUDA_CHECK(call) do { \
    cudaError_t err = (call); \
    if (err != cudaSuccess) { \
        jclass exc = env->FindClass("java/lang/RuntimeException"); \
        env->ThrowNew(exc, cudaGetErrorString(err)); \
        return -1; \
    } \
} while (0)

extern "C"
JNIEXPORT jint JNICALL Java_Noop_1gpu_runKernel(JNIEnv *env, jclass cls) {
    int *d_ptr;
    CUDA_CHECK(cudaMalloc(&d_ptr, sizeof(int)));
    CUDA_CHECK(cudaFree(d_ptr));
    return 0;
}
