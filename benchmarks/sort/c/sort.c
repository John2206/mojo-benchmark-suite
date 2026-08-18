#include <stdio.h>
#include <stdlib.h>

static unsigned int lcg_state;

static long lcg_next(void) {
    lcg_state = (lcg_state * 1103515245u + 12345u) & 0x7fffffffu;
    return (long)lcg_state;
}

int cmp(const void *a, const void *b) {
    long la = *(const long *)a, lb = *(const long *)b;
    return (la > lb) - (la < lb);
}

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 2000000;
    long *arr = malloc((size_t)n * sizeof(long));
    lcg_state = 42;
    for (long i = 0; i < n; i++) arr[i] = lcg_next();

    qsort(arr, n, sizeof(long), cmp);

    for (long i = 1; i < n; i++) {
        if (arr[i - 1] > arr[i]) {
            fprintf(stderr, "self-check failed: array not sorted\n");
            return 1;
        }
    }
    printf("%ld\n", arr[n - 1]);
    free(arr);
    return 0;
}
