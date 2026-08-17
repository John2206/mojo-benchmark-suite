#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static uint32_t crc32_table[256];

static void build_table(void) {
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t crc = i;
        for (int j = 0; j < 8; j++) {
            if (crc & 1) crc = (crc >> 1) ^ 0xEDB88320u;
            else crc >>= 1;
        }
        crc32_table[i] = crc;
    }
}

static uint32_t crc32_compute(const unsigned char *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < len; i++) {
        crc = crc32_table[(crc ^ data[i]) & 0xFF] ^ (crc >> 8);
    }
    return crc ^ 0xFFFFFFFFu;
}

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 50000000;

    build_table();

    if (crc32_compute((const unsigned char *)"", 0) != 0x00000000u) {
        fprintf(stderr, "self-check failed: CRC32(\"\") mismatch\n");
        return 1;
    }
    const unsigned char check[] = "123456789";
    if (crc32_compute(check, 9) != 0xCBF43926u) {
        fprintf(stderr, "self-check failed: CRC32(\"123456789\") mismatch\n");
        return 1;
    }

    unsigned char *buf = malloc((size_t)n);
    for (long i = 0; i < n; i++) buf[i] = (unsigned char)((i * 131 + 7) % 256);

    uint32_t result = crc32_compute(buf, (size_t)n);
    printf("%08x\n", result);

    free(buf);
    return 0;
}
