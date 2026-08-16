from std.sys import argv


def append_int(mut buf: List[Byte], val: Int):
    if val == 0:
        buf.append(48)
        return
    var digits = List[Byte]()
    var v = val
    while v > 0:
        digits.append(Byte(48 + (v % 10)))
        v //= 10
    for i in range(len(digits) - 1, -1, -1):
        buf.append(digits[i])


def append_str(mut buf: List[Byte], s: StringSlice):
    for b in s.bytes():
        buf.append(b)


def parse_int(buf: List[Byte], mut pos: Int) -> Int:
    var val = 0
    while pos < len(buf) and buf[pos] >= 48 and buf[pos] <= 57:
        val = val * 10 + Int(buf[pos] - 48)
        pos += 1
    return val


def parse_decimal1(buf: List[Byte], mut pos: Int) -> Float64:
    var whole = parse_int(buf, pos)
    pos += 1  # '.'
    var frac = Int(buf[pos] - 48)
    pos += 1
    return Float64(whole) + Float64(frac) / 10.0


def main() raises:
    var args = argv()
    var n = 200_000
    if len(args) > 1:
        n = atol(args[1])

    var buf = List[Byte]()
    buf.append(91)  # '['
    for i in range(n):
        if i > 0:
            buf.append(44)  # ','
        buf.append(123)  # '{'
        append_str(buf, "\"id\":")
        append_int(buf, i)
        append_str(buf, ",\"name\":\"item")
        append_int(buf, i)
        append_str(buf, "\",\"value\":")
        append_int(buf, i // 2)
        buf.append(46)  # '.'
        buf.append(Byte(48 + (i % 2) * 5))
        buf.append(125)  # '}'
    buf.append(93)  # ']'

    var pos = 1
    var id_sum = 0
    var decoded_count = 0
    while buf[pos] != 93:
        pos += 1  # '{'
        pos += 5  # "id":
        var id = parse_int(buf, pos)
        pos += 13  # ,"name":"item
        _ = parse_int(buf, pos)  # skip digits in name, not re-checked
        pos += 10  # ","value":
        var value = parse_decimal1(buf, pos)
        pos += 1  # '}'
        if pos < len(buf) and buf[pos] == 44:
            pos += 1

        if value != Float64(id) * 0.5:
            raise Error("self-check failed: decoded value mismatch")
        id_sum += id
        decoded_count += 1

    var expected_sum = n * (n - 1) // 2
    if id_sum != expected_sum or decoded_count != n:
        raise Error("self-check failed: id sum or count mismatch")

    print(id_sum)
