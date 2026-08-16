#include <stdio.h>
#include <stdlib.h>
#include <immintrin.h>

#define MAX_ITER 1000
#define W 4

__attribute__((target("avx2")))
static void escape_counts_row(const double cr[W], double ci, long iters_out[W]) {
    __m256d zr = _mm256_setzero_pd();
    __m256d zi = _mm256_setzero_pd();
    __m256d cr_vec = _mm256_loadu_pd(cr);
    __m256d ci_vec = _mm256_set1_pd(ci);
    __m256d four = _mm256_set1_pd(4.0);
    __m256i iters = _mm256_setzero_si256();
    __m256i active = _mm256_set1_epi64x(-1);

    for (int i = 0; i < MAX_ITER; i++) {
        __m256d zr2 = _mm256_mul_pd(zr, zr);
        __m256d zi2 = _mm256_mul_pd(zi, zi);
        __m256d mag2 = _mm256_add_pd(zr2, zi2);
        __m256i cmp = _mm256_castpd_si256(_mm256_cmp_pd(mag2, four, _CMP_LE_OQ));
        __m256i still = _mm256_and_si256(cmp, active);

        if (_mm256_testz_si256(still, still)) break;

        __m256d new_zi = _mm256_add_pd(_mm256_mul_pd(_mm256_set1_pd(2.0), _mm256_mul_pd(zr, zi)), ci_vec);
        __m256d new_zr = _mm256_add_pd(_mm256_sub_pd(zr2, zi2), cr_vec);
        __m256d still_d = _mm256_castsi256_pd(still);
        zr = _mm256_blendv_pd(zr, new_zr, still_d);
        zi = _mm256_blendv_pd(zi, new_zi, still_d);

        __m256i iters_plus1 = _mm256_add_epi64(iters, _mm256_set1_epi64x(1));
        iters = _mm256_blendv_epi8(iters, iters_plus1, still);
        active = still;
    }

    _mm256_storeu_si256((__m256i *)iters_out, iters);
}

int main(int argc, char **argv) {
    __builtin_cpu_init();
    if (!__builtin_cpu_supports("avx2")) {
        fprintf(stderr, "AVX2 not supported on this CPU\n");
        return 1;
    }

    int n = argc > 1 ? atoi(argv[1]) : 800;

    double origin_cr[W] = {0.0, 0.0, 0.0, 0.0};
    long origin_iters[W];
    escape_counts_row(origin_cr, 0.0, origin_iters);
    for (int lane = 0; lane < W; lane++) {
        if (origin_iters[lane] != MAX_ITER) {
            fprintf(stderr, "self-check failed: origin should never escape\n");
            return 1;
        }
    }

    double far_cr[W] = {2.0, 2.0, 2.0, 2.0};
    long far_iters[W];
    escape_counts_row(far_cr, 2.0, far_iters);
    for (int lane = 0; lane < W; lane++) {
        if (far_iters[lane] >= MAX_ITER) {
            fprintf(stderr, "self-check failed: far point should escape quickly\n");
            return 1;
        }
    }

    int groups = n / W;
    long count = 0;
    for (int py = 0; py < n; py++) {
        double ci = -1.5 + 3.0 * py / n;
        for (int gx = 0; gx < groups; gx++) {
            double cr[W];
            for (int lane = 0; lane < W; lane++) {
                int px = gx * W + lane;
                cr[lane] = -2.0 + 3.0 * px / n;
            }
            long iters[W];
            escape_counts_row(cr, ci, iters);
            for (int lane = 0; lane < W; lane++) {
                if (iters[lane] == MAX_ITER) count++;
            }
        }
    }

    printf("%ld\n", count);
    return 0;
}
