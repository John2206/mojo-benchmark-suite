#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define STEPS 100
#define G 1e-4
#define DT 1e-3

int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 300;

    double *mass = malloc((size_t)n * sizeof(double));
    double *px = malloc((size_t)n * sizeof(double));
    double *py = malloc((size_t)n * sizeof(double));
    double *pz = malloc((size_t)n * sizeof(double));
    double *vx = calloc((size_t)n, sizeof(double));
    double *vy = calloc((size_t)n, sizeof(double));
    double *vz = calloc((size_t)n, sizeof(double));

    for (int i = 0; i < n; i++) {
        mass[i] = 1.0 + i;
        px[i] = i * 0.1;
        py[i] = i * 0.2;
        pz[i] = i * 0.3;
    }

    for (int s = 0; s < STEPS; s++) {
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                double dx = px[j] - px[i];
                double dy = py[j] - py[i];
                double dz = pz[j] - pz[i];
                double dist2 = dx * dx + dy * dy + dz * dz + 1e-9;
                double inv_dist3 = 1.0 / (dist2 * sqrt(dist2));
                double fx = G * dx * inv_dist3;
                double fy = G * dy * inv_dist3;
                double fz = G * dz * inv_dist3;
                vx[i] += fx * mass[j] * DT;
                vy[i] += fy * mass[j] * DT;
                vz[i] += fz * mass[j] * DT;
                vx[j] -= fx * mass[i] * DT;
                vy[j] -= fy * mass[i] * DT;
                vz[j] -= fz * mass[i] * DT;
            }
        }
        for (int i = 0; i < n; i++) {
            px[i] += vx[i] * DT;
            py[i] += vy[i] * DT;
            pz[i] += vz[i] * DT;
        }
    }

    double momentum_x = 0.0;
    for (int i = 0; i < n; i++) momentum_x += mass[i] * vx[i];
    if (fabs(momentum_x) > 1e-6) {
        fprintf(stderr, "self-check failed: momentum not conserved (%.9f)\n", momentum_x);
        return 1;
    }

    printf("%.6f %.6f %.6f\n", px[0], py[0], pz[0]);
    return 0;
}
