from std.sys import argv
from std.bit import rotate_bits_right

comptime HEX_DIGITS = "0123456789abcdef"


def sha256_k() -> List[UInt32]:
    return [
        UInt32(0x428a2f98), UInt32(0x71374491), UInt32(0xb5c0fbcf), UInt32(0xe9b5dba5),
        UInt32(0x3956c25b), UInt32(0x59f111f1), UInt32(0x923f82a4), UInt32(0xab1c5ed5),
        UInt32(0xd807aa98), UInt32(0x12835b01), UInt32(0x243185be), UInt32(0x550c7dc3),
        UInt32(0x72be5d74), UInt32(0x80deb1fe), UInt32(0x9bdc06a7), UInt32(0xc19bf174),
        UInt32(0xe49b69c1), UInt32(0xefbe4786), UInt32(0x0fc19dc6), UInt32(0x240ca1cc),
        UInt32(0x2de92c6f), UInt32(0x4a7484aa), UInt32(0x5cb0a9dc), UInt32(0x76f988da),
        UInt32(0x983e5152), UInt32(0xa831c66d), UInt32(0xb00327c8), UInt32(0xbf597fc7),
        UInt32(0xc6e00bf3), UInt32(0xd5a79147), UInt32(0x06ca6351), UInt32(0x14292967),
        UInt32(0x27b70a85), UInt32(0x2e1b2138), UInt32(0x4d2c6dfc), UInt32(0x53380d13),
        UInt32(0x650a7354), UInt32(0x766a0abb), UInt32(0x81c2c92e), UInt32(0x92722c85),
        UInt32(0xa2bfe8a1), UInt32(0xa81a664b), UInt32(0xc24b8b70), UInt32(0xc76c51a3),
        UInt32(0xd192e819), UInt32(0xd6990624), UInt32(0xf40e3585), UInt32(0x106aa070),
        UInt32(0x19a4c116), UInt32(0x1e376c08), UInt32(0x2748774c), UInt32(0x34b0bcb5),
        UInt32(0x391c0cb3), UInt32(0x4ed8aa4a), UInt32(0x5b9cca4f), UInt32(0x682e6ff3),
        UInt32(0x748f82ee), UInt32(0x78a5636f), UInt32(0x84c87814), UInt32(0x8cc70208),
        UInt32(0x90befffa), UInt32(0xa4506ceb), UInt32(0xbef9a3f7), UInt32(0xc67178f2),
    ]


def sha256_h0() -> List[UInt32]:
    return [
        UInt32(0x6a09e667), UInt32(0xbb67ae85), UInt32(0x3c6ef372), UInt32(0xa54ff53a),
        UInt32(0x510e527f), UInt32(0x9b05688c), UInt32(0x1f83d9ab), UInt32(0x5be0cd19),
    ]


def sha256(k: List[UInt32], msg: List[UInt8]) -> List[UInt8]:
    var h = sha256_h0()

    var msg_len = len(msg)
    var bit_len = UInt64(msg_len) * UInt64(8)
    var padded_len = ((msg_len + 9 + 63) // 64) * 64

    var msg2 = List[UInt8](length=padded_len, fill=UInt8(0))
    for i in range(msg_len):
        msg2[i] = msg[i]
    msg2[msg_len] = UInt8(0x80)
    for i in range(8):
        var shift = UInt64(8 * i)
        msg2[padded_len - 1 - i] = UInt8((bit_len >> shift) & UInt64(0xFF))

    var chunk = 0
    while chunk < padded_len:
        var w = List[UInt32](length=64, fill=UInt32(0))
        for i in range(16):
            var base = chunk + i * 4
            w[i] = (UInt32(msg2[base]) << UInt32(24)) | (UInt32(msg2[base + 1]) << UInt32(16)) | (UInt32(msg2[base + 2]) << UInt32(8)) | UInt32(msg2[base + 3])
        for i in range(16, 64):
            var s0 = rotate_bits_right[7](w[i - 15]) ^ rotate_bits_right[18](w[i - 15]) ^ (w[i - 15] >> UInt32(3))
            var s1 = rotate_bits_right[17](w[i - 2]) ^ rotate_bits_right[19](w[i - 2]) ^ (w[i - 2] >> UInt32(10))
            w[i] = w[i - 16] + s0 + w[i - 7] + s1

        var a = h[0]
        var b = h[1]
        var c = h[2]
        var d = h[3]
        var e = h[4]
        var f = h[5]
        var g = h[6]
        var hh = h[7]

        for i in range(64):
            var s1 = rotate_bits_right[6](e) ^ rotate_bits_right[11](e) ^ rotate_bits_right[25](e)
            var ch = (e & f) ^ ((~e) & g)
            var temp1 = hh + s1 + ch + k[i] + w[i]
            var s0 = rotate_bits_right[2](a) ^ rotate_bits_right[13](a) ^ rotate_bits_right[22](a)
            var maj = (a & b) ^ (a & c) ^ (b & c)
            var temp2 = s0 + maj
            hh = g
            g = f
            f = e
            e = d + temp1
            d = c
            c = b
            b = a
            a = temp1 + temp2

        h[0] = h[0] + a
        h[1] = h[1] + b
        h[2] = h[2] + c
        h[3] = h[3] + d
        h[4] = h[4] + e
        h[5] = h[5] + f
        h[6] = h[6] + g
        h[7] = h[7] + hh

        chunk += 64

    var out = List[UInt8](length=32, fill=UInt8(0))
    for i in range(8):
        out[i * 4] = UInt8((h[i] >> UInt32(24)) & UInt32(0xFF))
        out[i * 4 + 1] = UInt8((h[i] >> UInt32(16)) & UInt32(0xFF))
        out[i * 4 + 2] = UInt8((h[i] >> UInt32(8)) & UInt32(0xFF))
        out[i * 4 + 3] = UInt8(h[i] & UInt32(0xFF))
    return out^


def to_hex(data: List[UInt8]) -> String:
    var result = String("")
    for b in data:
        var hi = Int(b >> UInt8(4))
        var lo = Int(b & UInt8(0xF))
        result += String(HEX_DIGITS[byte=hi])
        result += String(HEX_DIGITS[byte=lo])
    return result


def main() raises:
    var args = argv()
    var n = 2_000_000
    if len(args) > 1:
        n = atol(args[1])

    var k = sha256_k()

    var empty = List[UInt8]()
    if to_hex(sha256(k, empty)) != "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855":
        raise Error('self-check failed: SHA256("") mismatch')

    var abc: List[UInt8] = [UInt8(ord("a")), UInt8(ord("b")), UInt8(ord("c"))]
    if to_hex(sha256(k, abc)) != "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad":
        raise Error('self-check failed: SHA256("abc") mismatch')

    var buf = List[UInt8](length=n, fill=UInt8(0))
    for i in range(n):
        buf[i] = UInt8((i * 131 + 7) % 256)

    print(to_hex(sha256(k, buf)))
