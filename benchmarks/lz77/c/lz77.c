#include <stdio.h>
#include <stdlib.h>

#define WINDOW 4096
#define MAX_MATCH 255
#define MIN_MATCH 3
#define HASH_SIZE 8192

typedef struct {
    int is_match;
    int offset;
    int length;
    unsigned char literal;
} Token;

static int hash3(const unsigned char *data, long i) {
    return ((data[i] * 131 + data[i + 1]) * 131 + data[i + 2]) & (HASH_SIZE - 1);
}

static Token *lz77_encode(const unsigned char *data, long n, long *out_count) {
    long *hash_table = malloc(HASH_SIZE * sizeof(long));
    for (int i = 0; i < HASH_SIZE; i++) hash_table[i] = -1;

    Token *tokens = malloc((size_t)n * sizeof(Token));
    long count = 0;
    long i = 0;
    while (i < n) {
        int best_len = 0;
        long best_cand = -1;
        if (i + 3 <= n) {
            int h = hash3(data, i);
            long cand = hash_table[h];
            if (cand != -1 && i - cand <= WINDOW) {
                int match_len = 0;
                while (match_len < MAX_MATCH && i + match_len < n && data[cand + match_len] == data[i + match_len]) {
                    match_len++;
                }
                if (match_len >= MIN_MATCH) {
                    best_len = match_len;
                    best_cand = cand;
                }
            }
            hash_table[h] = i;
        }
        if (best_len >= MIN_MATCH) {
            tokens[count].is_match = 1;
            tokens[count].offset = (int)(i - best_cand);
            tokens[count].length = best_len;
            tokens[count].literal = 0;
            count++;
            i += best_len;
        } else {
            tokens[count].is_match = 0;
            tokens[count].offset = 0;
            tokens[count].length = 0;
            tokens[count].literal = data[i];
            count++;
            i += 1;
        }
    }

    free(hash_table);
    *out_count = count;
    return tokens;
}

static unsigned char *lz77_decode(const Token *tokens, long count, long *out_len) {
    long capacity = 64;
    unsigned char *out = malloc((size_t)capacity);
    long len = 0;
    for (long t = 0; t < count; t++) {
        if (tokens[t].is_match) {
            long start = len - tokens[t].offset;
            for (int k = 0; k < tokens[t].length; k++) {
                if (len >= capacity) {
                    capacity *= 2;
                    out = realloc(out, (size_t)capacity);
                }
                out[len] = out[start + k];
                len++;
            }
        } else {
            if (len >= capacity) {
                capacity *= 2;
                out = realloc(out, (size_t)capacity);
            }
            out[len] = tokens[t].literal;
            len++;
        }
    }
    *out_len = len;
    return out;
}

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 5000000;

    unsigned char *data = malloc((size_t)n);
    unsigned char pattern[64];
    for (int i = 0; i < 64; i++) pattern[i] = (unsigned char)((i * 7 + 3) % 251);
    for (long i = 0; i < n; i++) {
        unsigned char v = pattern[i % 64];
        if (i % 97 == 0) v = (unsigned char)((v + 1) % 256);
        data[i] = v;
    }

    long token_count;
    Token *tokens = lz77_encode(data, n, &token_count);

    long decoded_len;
    unsigned char *decoded = lz77_decode(tokens, token_count, &decoded_len);

    if (decoded_len != n) {
        fprintf(stderr, "self-check failed: roundtrip length mismatch\n");
        return 1;
    }
    for (long i = 0; i < n; i++) {
        if (decoded[i] != data[i]) {
            fprintf(stderr, "self-check failed: roundtrip byte mismatch at %ld\n", i);
            return 1;
        }
    }

    long compressed_bytes = 0;
    for (long t = 0; t < token_count; t++) {
        compressed_bytes += tokens[t].is_match ? 4 : 2;
    }

    printf("%ld\n", compressed_bytes);

    free(data);
    free(tokens);
    free(decoded);
    return 0;
}
