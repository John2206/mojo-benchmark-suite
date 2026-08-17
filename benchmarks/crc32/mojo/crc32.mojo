from std.sys import argv

comptime HEX_DIGITS = "0123456789abcdef"


def to_hex8(value: UInt32) -> String:
    var result = String("")
    for i in range(8):
        var shift = UInt32((7 - i) * 4)
        var nibble = Int((value >> shift) & UInt32(0xF))
        result += String(HEX_DIGITS[byte=nibble])
    return result


def build_table() -> List[UInt32]:
    var table = List[UInt32](length=256, fill=UInt32(0))
    for i in range(256):
        var crc = UInt32(i)
        for _ in range(8):
            if (crc & UInt32(1)) != UInt32(0):
                crc = (crc >> UInt32(1)) ^ UInt32(0xEDB88320)
            else:
                crc = crc >> UInt32(1)
        table[i] = crc
    return table^


def crc32_compute(table: List[UInt32], data: List[UInt8]) -> UInt32:
    var crc: UInt32 = 0xFFFFFFFF
    for b in data:
        var idx = Int((crc ^ UInt32(b)) & UInt32(0xFF))
        crc = table[idx] ^ (crc >> UInt32(8))
    return crc ^ UInt32(0xFFFFFFFF)


def main() raises:
    var args = argv()
    var n = 50_000_000
    if len(args) > 1:
        n = atol(args[1])

    var table = build_table()

    var empty = List[UInt8]()
    if crc32_compute(table, empty) != UInt32(0):
        raise Error("self-check failed: CRC32(\"\") mismatch")

    var check: List[UInt8] = [49, 50, 51, 52, 53, 54, 55, 56, 57]
    if crc32_compute(table, check) != UInt32(0xCBF43926):
        raise Error("self-check failed: CRC32(\"123456789\") mismatch")

    var buf = List[UInt8](length=n, fill=UInt8(0))
    for i in range(n):
        buf[i] = UInt8((i * 131 + 7) % 256)

    var result = crc32_compute(table, buf)
    print(to_hex8(result))
