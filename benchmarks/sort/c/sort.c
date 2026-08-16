#include <stdio.h>
#include <stdlib.h>

int cmp(const void *a, const void *b) {
    int ia = *(const int *)a, ib = *(const int *)b;
    return (ia > ib) - (ia < ib);
}

int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 2000000;
    int *arr = malloc((size_t)n * sizeof(int));
    srand(42);
    for (int i = 0; i < n; i++) arr[i] = rand();

    qsort(arr, n, sizeof(int), cmp);

    for (int i = 1; i < n; i++) {
        if (arr[i - 1] > arr[i]) {
            fprintf(stderr, "self-check failed: array not sorted\n");
            return 1;
        }
    }
    printf("%d\n", arr[n - 1]);
    free(arr);
    return 0;
}
