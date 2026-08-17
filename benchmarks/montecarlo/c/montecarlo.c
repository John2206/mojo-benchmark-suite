#include <stdio.h>
#include <stdlib.h>
#include <math.h>

static unsigned int lcg_state;

static double lcg_next(void) {
    lcg_state = (lcg_state * 1103515245u + 12345u) & 0x7fffffffu;
    return (double)lcg_state / 2147483648.0;
}

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 50000000;

    lcg_state = 1;
    long inside = 0;
    for (long i = 0; i < n; i++) {
        double x = lcg_next();
        double y = lcg_next();
        if (x * x + y * y <= 1.0) inside++;
    }

    double pi_estimate = 4.0 * (double)inside / (double)n;
    double tolerance = 10.0 / sqrt((double)n);

    if (fabs(pi_estimate - 3.14159265358979323846) >= tolerance) {
        fprintf(stderr, "self-check failed: pi estimate out of tolerance: %.6f\n", pi_estimate);
        return 1;
    }

    printf("%.6f\n", pi_estimate);
    return 0;
}
