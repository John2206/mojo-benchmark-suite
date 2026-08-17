#include <stdio.h>
#include <stdlib.h>
#include <math.h>

static long next_pow2(long n) {
    long p = 1;
    while (p < n) p <<= 1;
    return p;
}

static void fft(double *re, double *im, long n, int invert) {
    long j = 0;
    for (long i = 1; i < n; i++) {
        long bit = n >> 1;
        while (j & bit) {
            j ^= bit;
            bit >>= 1;
        }
        j ^= bit;
        if (i < j) {
            double tr = re[i]; re[i] = re[j]; re[j] = tr;
            double ti = im[i]; im[i] = im[j]; im[j] = ti;
        }
    }

    for (long length = 2; length <= n; length <<= 1) {
        double ang = 2.0 * M_PI / (double)length * (invert ? 1.0 : -1.0);
        double wlen_re = cos(ang);
        double wlen_im = sin(ang);
        for (long i = 0; i < n; i += length) {
            double w_re = 1.0, w_im = 0.0;
            for (long k = i; k < i + length / 2; k++) {
                double u_re = re[k], u_im = im[k];
                double v_re = re[k + length / 2] * w_re - im[k + length / 2] * w_im;
                double v_im = re[k + length / 2] * w_im + im[k + length / 2] * w_re;
                re[k] = u_re + v_re;
                im[k] = u_im + v_im;
                re[k + length / 2] = u_re - v_re;
                im[k + length / 2] = u_im - v_im;
                double nw_re = w_re * wlen_re - w_im * wlen_im;
                double nw_im = w_re * wlen_im + w_im * wlen_re;
                w_re = nw_re;
                w_im = nw_im;
            }
        }
    }

    if (invert) {
        for (long i = 0; i < n; i++) {
            re[i] /= (double)n;
            im[i] /= (double)n;
        }
    }
}

int main(int argc, char **argv) {
    long requested = argc > 1 ? atol(argv[1]) : 1048576;
    long n = next_pow2(requested);

    double *re = malloc((size_t)n * sizeof(double));
    double *im = malloc((size_t)n * sizeof(double));
    double *orig = malloc((size_t)n * sizeof(double));
    for (long i = 0; i < n; i++) {
        double v = (double)(i % 7) - 3.0;
        re[i] = v;
        im[i] = 0.0;
        orig[i] = v;
    }

    fft(re, im, n, 0);
    fft(re, im, n, 1);

    double max_err = 0.0;
    for (long i = 0; i < n; i++) {
        double err = fabs(re[i] - orig[i]);
        if (fabs(im[i]) > err) err = fabs(im[i]);
        if (err > max_err) max_err = err;
    }

    if (max_err >= 1e-6) {
        fprintf(stderr, "self-check failed: roundtrip reconstruction error too large: %e\n", max_err);
        return 1;
    }

    printf("%e\n", max_err);

    free(re);
    free(im);
    free(orig);
    return 0;
}
