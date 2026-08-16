#include <stdio.h>
#include <stdlib.h>

#define MAX_ITER 1000

int escape_iters(double cr, double ci) {
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

int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 800;

    if (escape_iters(0.0, 0.0) != MAX_ITER) {
        fprintf(stderr, "self-check failed: origin should never escape\n");
        return 1;
    }
    if (escape_iters(2.0, 2.0) >= MAX_ITER) {
        fprintf(stderr, "self-check failed: far point should escape quickly\n");
        return 1;
    }

    long count = 0;
    for (int py = 0; py < n; py++) {
        double ci = -1.5 + 3.0 * py / n;
        for (int px = 0; px < n; px++) {
            double cr = -2.0 + 3.0 * px / n;
            if (escape_iters(cr, ci) == MAX_ITER) count++;
        }
    }
    printf("%ld\n", count);
    return 0;
}
