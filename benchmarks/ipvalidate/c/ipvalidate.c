#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned int lcg_state;

static long lcg_next(void) {
    lcg_state = (lcg_state * 1103515245u + 12345u) & 0x7fffffffu;
    return (long)lcg_state;
}

int parse_group(const char *s, int len) {
    if (len < 1 || len > 3) return -1;
    int val = 0;
    for (int i = 0; i < len; i++) {
        char c = s[i];
        if (c < '0' || c > '9') return -1;
        val = val * 10 + (c - '0');
    }
    if (val > 255) return -1;
    return val;
}

int is_valid_ip(const char *s) {
    int parts = 0;
    const char *start = s;
    for (const char *p = s; ; p++) {
        if (*p == '.' || *p == '\0') {
            int len = (int)(p - start);
            if (parse_group(start, len) < 0) return 0;
            parts++;
            if (*p == '\0') break;
            start = p + 1;
        }
    }
    return parts == 4;
}

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 2000000;

    if (!is_valid_ip("192.168.1.1")) {
        fprintf(stderr, "self-check failed: known-valid IP rejected\n");
        return 1;
    }
    if (is_valid_ip("999.1.1.1")) {
        fprintf(stderr, "self-check failed: known-invalid IP accepted\n");
        return 1;
    }
    if (is_valid_ip("1.2.3")) {
        fprintf(stderr, "self-check failed: known-invalid IP accepted\n");
        return 1;
    }

    lcg_state = 42;
    long valid = 0;
    char buf[32];
    for (long i = 0; i < n; i++) {
        int max_val = (lcg_next() % 10 < 7) ? 255 : 999;
        int a = (int)(lcg_next() % (max_val + 1));
        int b = (int)(lcg_next() % (max_val + 1));
        int c = (int)(lcg_next() % (max_val + 1));
        int d = (int)(lcg_next() % (max_val + 1));
        snprintf(buf, sizeof(buf), "%d.%d.%d.%d", a, b, c, d);
        if (is_valid_ip(buf)) valid++;
    }

    printf("%ld\n", valid);
    return 0;
}
