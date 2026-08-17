import sys

K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]

MASK = 0xFFFFFFFF


def rotr(x, n):
    return ((x >> n) | (x << (32 - n))) & MASK


def sha256(msg):
    h = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ]

    bit_len = len(msg) * 8
    padded_len = ((len(msg) + 9 + 63) // 64) * 64
    msg2 = bytearray(padded_len)
    msg2[: len(msg)] = msg
    msg2[len(msg)] = 0x80
    for i in range(8):
        msg2[padded_len - 1 - i] = (bit_len >> (8 * i)) & 0xFF

    for chunk in range(0, padded_len, 64):
        w = [0] * 64
        for i in range(16):
            base = chunk + i * 4
            w[i] = (msg2[base] << 24) | (msg2[base + 1] << 16) | (msg2[base + 2] << 8) | msg2[base + 3]
        for i in range(16, 64):
            s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >> 3)
            s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >> 10)
            w[i] = (w[i - 16] + s0 + w[i - 7] + s1) & MASK

        a, b, c, d, e, f, g, hh = h

        for i in range(64):
            s1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)
            ch = (e & f) ^ ((~e & MASK) & g)
            temp1 = (hh + s1 + ch + K[i] + w[i]) & MASK
            s0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (s0 + maj) & MASK
            hh, g, f = g, f, e
            e = (d + temp1) & MASK
            d, c, b = c, b, a
            a = (temp1 + temp2) & MASK

        h[0] = (h[0] + a) & MASK
        h[1] = (h[1] + b) & MASK
        h[2] = (h[2] + c) & MASK
        h[3] = (h[3] + d) & MASK
        h[4] = (h[4] + e) & MASK
        h[5] = (h[5] + f) & MASK
        h[6] = (h[6] + g) & MASK
        h[7] = (h[7] + hh) & MASK

    return b"".join(v.to_bytes(4, "big") for v in h)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000

    assert sha256(b"").hex() == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 'self-check failed: SHA256("") mismatch'
    assert sha256(b"abc").hex() == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", 'self-check failed: SHA256("abc") mismatch'

    buf = bytes((i * 131 + 7) % 256 for i in range(n))

    print(sha256(buf).hex())


if __name__ == "__main__":
    main()
