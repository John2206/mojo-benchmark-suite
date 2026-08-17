import sys

WINDOW = 4096
MAX_MATCH = 255
MIN_MATCH = 3
HASH_SIZE = 8192


def hash3(data, i):
    return ((data[i] * 131 + data[i + 1]) * 131 + data[i + 2]) & (HASH_SIZE - 1)


def lz77_encode(data):
    n = len(data)
    hash_table = [-1] * HASH_SIZE
    tokens = []
    i = 0
    while i < n:
        best_len = 0
        best_cand = -1
        if i + 3 <= n:
            h = hash3(data, i)
            cand = hash_table[h]
            if cand != -1 and i - cand <= WINDOW:
                match_len = 0
                while match_len < MAX_MATCH and i + match_len < n and data[cand + match_len] == data[i + match_len]:
                    match_len += 1
                if match_len >= MIN_MATCH:
                    best_len = match_len
                    best_cand = cand
            hash_table[h] = i
        if best_len >= MIN_MATCH:
            tokens.append((True, i - best_cand, best_len, 0))
            i += best_len
        else:
            tokens.append((False, 0, 0, data[i]))
            i += 1
    return tokens


def lz77_decode(tokens):
    out = bytearray()
    for is_match, offset, length, literal in tokens:
        if is_match:
            start = len(out) - offset
            for k in range(length):
                out.append(out[start + k])
        else:
            out.append(literal)
    return bytes(out)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5_000_000

    pattern = bytes((i * 7 + 3) % 251 for i in range(64))
    data = bytearray(n)
    for i in range(n):
        v = pattern[i % 64]
        if i % 97 == 0:
            v = (v + 1) % 256
        data[i] = v
    data = bytes(data)

    tokens = lz77_encode(data)
    decoded = lz77_decode(tokens)

    assert decoded == data, "self-check failed: roundtrip mismatch"

    compressed_bytes = sum(4 if t[0] else 2 for t in tokens)
    print(compressed_bytes)


if __name__ == "__main__":
    main()
