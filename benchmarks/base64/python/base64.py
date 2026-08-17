import sys

ENC_TABLE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def b64_encode(data):
    out = []
    n = len(data)
    i = 0
    while i + 3 <= n:
        b0, b1, b2 = data[i], data[i + 1], data[i + 2]
        out.append(ENC_TABLE[b0 >> 2])
        out.append(ENC_TABLE[((b0 & 0x03) << 4) | (b1 >> 4)])
        out.append(ENC_TABLE[((b1 & 0x0F) << 2) | (b2 >> 6)])
        out.append(ENC_TABLE[b2 & 0x3F])
        i += 3
    rem = n - i
    if rem == 1:
        b0 = data[i]
        out.append(ENC_TABLE[b0 >> 2])
        out.append(ENC_TABLE[(b0 & 0x03) << 4])
        out.append("==")
    elif rem == 2:
        b0, b1 = data[i], data[i + 1]
        out.append(ENC_TABLE[b0 >> 2])
        out.append(ENC_TABLE[((b0 & 0x03) << 4) | (b1 >> 4)])
        out.append(ENC_TABLE[(b1 & 0x0F) << 2])
        out.append("=")
    return "".join(out)


def dec_value(c):
    if "A" <= c <= "Z":
        return ord(c) - ord("A")
    if "a" <= c <= "z":
        return ord(c) - ord("a") + 26
    if "0" <= c <= "9":
        return ord(c) - ord("0") + 52
    if c == "+":
        return 62
    if c == "/":
        return 63
    return -1


def b64_decode(enc):
    out = bytearray()
    for i in range(0, len(enc), 4):
        v0 = dec_value(enc[i])
        v1 = dec_value(enc[i + 1])
        v2 = -2 if enc[i + 2] == "=" else dec_value(enc[i + 2])
        v3 = -2 if enc[i + 3] == "=" else dec_value(enc[i + 3])
        out.append(((v0 << 2) | (v1 >> 4)) & 0xFF)
        if v2 != -2:
            out.append((((v1 & 0x0F) << 4) | (v2 >> 2)) & 0xFF)
            if v3 != -2:
                out.append((((v2 & 0x03) << 6) | v3) & 0xFF)
    return bytes(out)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20_000_000

    assert b64_encode(b"") == "", 'self-check failed: base64("") mismatch'
    assert b64_encode(b"f") == "Zg==", 'self-check failed: base64("f") mismatch'
    assert b64_encode(b"fo") == "Zm8=", 'self-check failed: base64("fo") mismatch'
    assert b64_encode(b"foo") == "Zm9v", 'self-check failed: base64("foo") mismatch'

    buf = bytes((i * 131 + 7) % 256 for i in range(n))

    encoded = b64_encode(buf)
    decoded = b64_decode(encoded)
    assert decoded == buf, "self-check failed: roundtrip mismatch"

    print(sum(ord(c) for c in encoded))


if __name__ == "__main__":
    main()
