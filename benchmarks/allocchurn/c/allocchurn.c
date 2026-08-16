#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 5000000;

    long total = 0;
    for (long i = 0; i < n; i++) {
        int *arr = malloc(64 * sizeof(int));
        for (int j = 0; j < 64; j++) arr[j] = j;
        long sum = 0;
        for (int j = 0; j < 64; j++) sum += arr[j];
        total += sum;
        free(arr);
    }

    if (total != n * 2016L) {
        fprintf(stderr, "self-check failed: total mismatch\n");
        return 1;
    }

    printf("%ld\n", total);
    return 0;
}
