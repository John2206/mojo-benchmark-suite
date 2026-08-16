#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 400;
    double *a = malloc((size_t)n * n * sizeof(double));
    double *b = malloc((size_t)n * n * sizeof(double));
    double *c = calloc((size_t)n * n, sizeof(double));

    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            a[i * n + j] = (double)((i * 3 + j) % 13);
            b[i * n + j] = (double)((i + j * 2) % 17);
        }

    for (int i = 0; i < n; i++)
        for (int k = 0; k < n; k++) {
            double aik = a[i * n + k];
            for (int j = 0; j < n; j++)
                c[i * n + j] += aik * b[k * n + j];
        }

    double expected = 0.0;
    for (int k = 0; k < n; k++)
        expected += a[k] * b[k * n];
    if (c[0] != expected) {
        fprintf(stderr, "self-check failed: c[0][0] mismatch\n");
        return 1;
    }

    printf("%.2f\n", c[(size_t)(n - 1) * n + (n - 1)]);
    free(a);
    free(b);
    free(c);
    return 0;
}
