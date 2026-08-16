#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define VOCAB_SIZE 20
#define TABLE_CAP 64 /* power of two, > 2x VOCAB_SIZE keeps collisions low */

static const char *VOCAB[VOCAB_SIZE] = {
    "the", "of", "and", "a", "to", "in", "is", "you", "that", "it",
    "he", "was", "for", "on", "are", "as", "with", "his", "they", "at"
};

typedef struct {
    const char *key; /* NULL = empty slot */
    long count;
} Slot;

/* C has no stdlib hash map, so this benchmark writes the small
 * open-addressing table you'd actually reach for in real C code. */
unsigned long hash_str(const char *s) {
    unsigned long h = 5381;
    int c;
    while ((c = *s++)) h = ((h << 5) + h) + (unsigned long)c;
    return h;
}

void table_incr(Slot *table, const char *key) {
    unsigned long i = hash_str(key) & (TABLE_CAP - 1);
    while (table[i].key != NULL && strcmp(table[i].key, key) != 0) {
        i = (i + 1) & (TABLE_CAP - 1);
    }
    table[i].key = key;
    table[i].count++;
}

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 2000000;

    Slot table[TABLE_CAP] = {0};
    srand(42);
    for (long k = 0; k < n; k++) {
        int idx = rand() % VOCAB_SIZE;
        table_incr(table, VOCAB[idx]);
    }

    long total = 0;
    int distinct = 0;
    for (int i = 0; i < TABLE_CAP; i++) {
        if (table[i].key != NULL) {
            total += table[i].count;
            distinct++;
        }
    }
    if (total != n) {
        fprintf(stderr, "self-check failed: counts do not sum to n\n");
        return 1;
    }

    printf("%d\n", distinct);
    return 0;
}
