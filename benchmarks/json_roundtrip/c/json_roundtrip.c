#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static long parse_int(const char *s, int *pos) {
    long val = 0;
    while (s[*pos] >= '0' && s[*pos] <= '9') {
        val = val * 10 + (s[*pos] - '0');
        (*pos)++;
    }
    return val;
}

static double parse_decimal1(const char *s, int *pos) {
    long whole = parse_int(s, pos);
    (*pos)++; /* skip '.' */
    int frac = s[*pos] - '0';
    (*pos)++;
    return (double)whole + frac / 10.0;
}

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 200000;

    /* --- encode --- */
    /* per record: fixed literal chars (~32) + id digits (appears twice) +
     * value digits (~= id digits) + 1 fractional digit; scale with n's
     * digit width so this stays correct for any --size, not just the default */
    int max_digits = 1;
    for (long tmp = n > 0 ? n - 1 : 0; tmp >= 10; tmp /= 10) max_digits++;
    size_t cap = (size_t)n * (size_t)(40 + 3 * max_digits) + 16;
    char *buf = malloc(cap);
    size_t len = 0;
    buf[len++] = '[';
    for (long i = 0; i < n; i++) {
        if (i > 0) buf[len++] = ',';
        len += snprintf(buf + len, cap - len, "{\"id\":%ld,\"name\":\"item%ld\",\"value\":%.1f}", i, i, i * 0.5);
    }
    buf[len++] = ']';
    buf[len] = '\0';

    /* --- decode --- */
    int pos = 1; /* skip '[' */
    long id_sum = 0;
    long decoded_count = 0;
    while (buf[pos] != ']') {
        pos += 1;               /* '{' */
        pos += (int)strlen("\"id\":");
        long id = parse_int(buf, &pos);
        pos += (int)strlen(",\"name\":\"item");
        parse_int(buf, &pos);   /* skip digits in name, not re-checked */
        pos += (int)strlen("\",\"value\":");
        double value = parse_decimal1(buf, &pos);
        pos += 1;               /* '}' */
        if (buf[pos] == ',') pos++;

        if (value != id * 0.5) {
            fprintf(stderr, "self-check failed: decoded value mismatch for id %ld\n", id);
            return 1;
        }
        id_sum += id;
        decoded_count++;
    }

    long expected_sum = n * (n - 1) / 2;
    if (id_sum != expected_sum || decoded_count != n) {
        fprintf(stderr, "self-check failed: id sum or count mismatch\n");
        return 1;
    }

    printf("%ld\n", id_sum);
    free(buf);
    return 0;
}
