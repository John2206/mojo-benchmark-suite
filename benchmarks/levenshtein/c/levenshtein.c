#include <stdio.h>
#include <stdlib.h>

static int edit_distance(const char *s1, int len1, const char *s2, int len2) {
    int *prev = malloc((size_t)(len2 + 1) * sizeof(int));
    int *cur = malloc((size_t)(len2 + 1) * sizeof(int));
    for (int j = 0; j <= len2; j++) prev[j] = j;

    for (int i = 1; i <= len1; i++) {
        cur[0] = i;
        for (int j = 1; j <= len2; j++) {
            int cost = (s1[i - 1] == s2[j - 1]) ? 0 : 1;
            int del = prev[j] + 1;
            int ins = cur[j - 1] + 1;
            int sub = prev[j - 1] + cost;
            int m = del < ins ? del : ins;
            if (sub < m) m = sub;
            cur[j] = m;
        }
        int *tmp = prev; prev = cur; cur = tmp;
    }

    int result = prev[len2];
    free(prev);
    free(cur);
    return result;
}

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 5000;

    if (edit_distance("kitten", 6, "sitting", 7) != 3) {
        fprintf(stderr, "self-check failed: edit_distance(kitten,sitting) mismatch\n");
        return 1;
    }

    const char alphabet[] = "ACGT";
    char *s1 = malloc((size_t)n);
    char *s2 = malloc((size_t)n);
    for (long i = 0; i < n; i++) {
        int base = (int)((i * 7 + 3) % 4);
        s1[i] = alphabet[base];
        s2[i] = (i % 5 == 4) ? alphabet[(base + 1) % 4] : alphabet[base];
    }

    int dist = edit_distance(s1, (int)n, s2, (int)n);
    printf("%d\n", dist);

    free(s1);
    free(s2);
    return 0;
}
