import sys


def build_table():
    table = [0] * 256
    for i in range(256):
        crc = i
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xEDB88320
            else:
                crc >>= 1
        table[i] = crc
    return table


def crc32_compute(table, data):
    crc = 0xFFFFFFFF
    for b in data:
        crc = table[(crc ^ b) & 0xFF] ^ (crc >> 8)
    return crc ^ 0xFFFFFFFF


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50_000_000

    table = build_table()

    assert crc32_compute(table, b"") == 0x00000000, 'self-check failed: CRC32("") mismatch'
    assert crc32_compute(table, b"123456789") == 0xCBF43926, 'self-check failed: CRC32("123456789") mismatch'

    buf = bytes((i * 131 + 7) % 256 for i in range(n))

    result = crc32_compute(table, buf)
    print(f"{result:08x}")


if __name__ == "__main__":
    main()
