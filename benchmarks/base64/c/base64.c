#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const char ENC_TABLE[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

static char *base64_encode(const unsigned char *data, size_t len, size_t *out_len) {
    size_t enc_len = ((len + 2) / 3) * 4;
    char *out = malloc(enc_len + 1);
    size_t i = 0, j = 0;
    while (i + 3 <= len) {
        unsigned char b0 = data[i], b1 = data[i + 1], b2 = data[i + 2];
        out[j++] = ENC_TABLE[b0 >> 2];
        out[j++] = ENC_TABLE[((b0 & 0x03) << 4) | (b1 >> 4)];
        out[j++] = ENC_TABLE[((b1 & 0x0F) << 2) | (b2 >> 6)];
        out[j++] = ENC_TABLE[b2 & 0x3F];
        i += 3;
    }
    size_t rem = len - i;
    if (rem == 1) {
        unsigned char b0 = data[i];
        out[j++] = ENC_TABLE[b0 >> 2];
        out[j++] = ENC_TABLE[(b0 & 0x03) << 4];
        out[j++] = '=';
        out[j++] = '=';
    } else if (rem == 2) {
        unsigned char b0 = data[i], b1 = data[i + 1];
        out[j++] = ENC_TABLE[b0 >> 2];
        out[j++] = ENC_TABLE[((b0 & 0x03) << 4) | (b1 >> 4)];
        out[j++] = ENC_TABLE[(b1 & 0x0F) << 2];
        out[j++] = '=';
    }
    out[j] = '\0';
    *out_len = j;
    return out;
}

static int dec_value(unsigned char c) {
    if (c >= 'A' && c <= 'Z') return c - 'A';
    if (c >= 'a' && c <= 'z') return c - 'a' + 26;
    if (c >= '0' && c <= '9') return c - '0' + 52;
    if (c == '+') return 62;
    if (c == '/') return 63;
    return -1;
}

static unsigned char *base64_decode(const char *enc, size_t enc_len, size_t *out_len) {
    unsigned char *out = malloc((enc_len / 4) * 3 + 3);
    size_t j = 0;
    for (size_t i = 0; i < enc_len; i += 4) {
        int v0 = dec_value((unsigned char)enc[i]);
        int v1 = dec_value((unsigned char)enc[i + 1]);
        int v2 = (enc[i + 2] == '=') ? -2 : dec_value((unsigned char)enc[i + 2]);
        int v3 = (enc[i + 3] == '=') ? -2 : dec_value((unsigned char)enc[i + 3]);
        out[j++] = (unsigned char)((v0 << 2) | (v1 >> 4));
        if (v2 != -2) {
            out[j++] = (unsigned char)(((v1 & 0x0F) << 4) | (v2 >> 2));
            if (v3 != -2) {
                out[j++] = (unsigned char)(((v2 & 0x03) << 6) | v3);
            }
        }
    }
    *out_len = j;
    return out;
}

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 20000000;

    size_t elen;
    char *e;

    e = base64_encode((const unsigned char *)"", 0, &elen);
    if (elen != 0) { fprintf(stderr, "self-check failed: base64(\"\") mismatch\n"); return 1; }
    free(e);

    e = base64_encode((const unsigned char *)"f", 1, &elen);
    if (strcmp(e, "Zg==") != 0) { fprintf(stderr, "self-check failed: base64(\"f\") mismatch\n"); return 1; }
    free(e);

    e = base64_encode((const unsigned char *)"fo", 2, &elen);
    if (strcmp(e, "Zm8=") != 0) { fprintf(stderr, "self-check failed: base64(\"fo\") mismatch\n"); return 1; }
    free(e);

    e = base64_encode((const unsigned char *)"foo", 3, &elen);
    if (strcmp(e, "Zm9v") != 0) { fprintf(stderr, "self-check failed: base64(\"foo\") mismatch\n"); return 1; }
    free(e);

    unsigned char *buf = malloc((size_t)n);
    for (long i = 0; i < n; i++) buf[i] = (unsigned char)((i * 131 + 7) % 256);

    char *encoded = base64_encode(buf, (size_t)n, &elen);

    size_t dlen;
    unsigned char *decoded = base64_decode(encoded, elen, &dlen);
    if (dlen != (size_t)n || memcmp(decoded, buf, (size_t)n) != 0) {
        fprintf(stderr, "self-check failed: roundtrip mismatch\n");
        return 1;
    }

    long sum = 0;
    for (size_t i = 0; i < elen; i++) sum += (unsigned char)encoded[i];
    printf("%ld\n", sum);

    free(buf);
    free(encoded);
    free(decoded);
    return 0;
}
