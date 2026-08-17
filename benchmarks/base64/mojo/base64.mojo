from std.sys import argv


def str_bytes(s: String) -> List[UInt8]:
    var out = List[UInt8]()
    for b in s.as_bytes():
        out.append(b)
    return out^


def bytes_equal(a: List[UInt8], b: List[UInt8]) -> Bool:
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if a[i] != b[i]:
            return False
    return True


def base64_encode(enc_table: List[UInt8], data: List[UInt8]) -> List[UInt8]:
    var out = List[UInt8]()
    var n = len(data)
    var i = 0
    while i + 3 <= n:
        var b0 = data[i]
        var b1 = data[i + 1]
        var b2 = data[i + 2]
        out.append(enc_table[Int(b0 >> UInt8(2))])
        out.append(enc_table[Int(((b0 & UInt8(0x03)) << UInt8(4)) | (b1 >> UInt8(4)))])
        out.append(enc_table[Int(((b1 & UInt8(0x0F)) << UInt8(2)) | (b2 >> UInt8(6)))])
        out.append(enc_table[Int(b2 & UInt8(0x3F))])
        i += 3
    var rem = n - i
    var eq = UInt8(ord("="))
    if rem == 1:
        var b0 = data[i]
        out.append(enc_table[Int(b0 >> UInt8(2))])
        out.append(enc_table[Int((b0 & UInt8(0x03)) << UInt8(4))])
        out.append(eq)
        out.append(eq)
    elif rem == 2:
        var b0 = data[i]
        var b1 = data[i + 1]
        out.append(enc_table[Int(b0 >> UInt8(2))])
        out.append(enc_table[Int(((b0 & UInt8(0x03)) << UInt8(4)) | (b1 >> UInt8(4)))])
        out.append(enc_table[Int((b1 & UInt8(0x0F)) << UInt8(2))])
        out.append(eq)
    return out^


def dec_value(c: UInt8) -> Int:
    if c >= UInt8(ord("A")) and c <= UInt8(ord("Z")):
        return Int(c) - Int(ord("A"))
    if c >= UInt8(ord("a")) and c <= UInt8(ord("z")):
        return Int(c) - Int(ord("a")) + 26
    if c >= UInt8(ord("0")) and c <= UInt8(ord("9")):
        return Int(c) - Int(ord("0")) + 52
    if c == UInt8(ord("+")):
        return 62
    if c == UInt8(ord("/")):
        return 63
    return -1


def base64_decode(enc: List[UInt8]) -> List[UInt8]:
    var out = List[UInt8]()
    var eq = UInt8(ord("="))
    var i = 0
    var n = len(enc)
    while i < n:
        var v0 = dec_value(enc[i])
        var v1 = dec_value(enc[i + 1])
        var v2: Int = -2 if enc[i + 2] == eq else dec_value(enc[i + 2])
        var v3: Int = -2 if enc[i + 3] == eq else dec_value(enc[i + 3])
        out.append(UInt8((v0 << 2) | (v1 >> 4)))
        if v2 != -2:
            out.append(UInt8(((v1 & 0x0F) << 4) | (v2 >> 2)))
            if v3 != -2:
                out.append(UInt8(((v2 & 0x03) << 6) | v3))
        i += 4
    return out^


def main() raises:
    var args = argv()
    var n = 20_000_000
    if len(args) > 1:
        n = atol(args[1])

    var enc_table = str_bytes("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/")

    if len(base64_encode(enc_table, List[UInt8]())) != 0:
        raise Error('self-check failed: base64("") mismatch')
    if not bytes_equal(base64_encode(enc_table, str_bytes("f")), str_bytes("Zg==")):
        raise Error('self-check failed: base64("f") mismatch')
    if not bytes_equal(base64_encode(enc_table, str_bytes("fo")), str_bytes("Zm8=")):
        raise Error('self-check failed: base64("fo") mismatch')
    if not bytes_equal(base64_encode(enc_table, str_bytes("foo")), str_bytes("Zm9v")):
        raise Error('self-check failed: base64("foo") mismatch')

    var buf = List[UInt8](length=n, fill=UInt8(0))
    for i in range(n):
        buf[i] = UInt8((i * 131 + 7) % 256)

    var encoded = base64_encode(enc_table, buf)
    var decoded = base64_decode(encoded)
    if not bytes_equal(decoded, buf):
        raise Error("self-check failed: roundtrip mismatch")

    var total: UInt64 = 0
    for b in encoded:
        total += UInt64(b)
    print(total)
