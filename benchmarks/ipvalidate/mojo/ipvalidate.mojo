from std.sys import argv
from std.random import random_si64, seed


def parse_group(g: StringSlice) raises -> Int:
    var n = g.byte_length()
    if n < 1 or n > 3:
        return -1
    for byte in g.bytes():
        if byte < 48 or byte > 57:
            return -1
    var val = atol(g)
    if val > 255:
        return -1
    return val


def is_valid_ip(s: String) raises -> Bool:
    var parts = s.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if parse_group(part) < 0:
            return False
    return True


def main() raises:
    var args = argv()
    var n = 2_000_000
    if len(args) > 1:
        n = atol(args[1])

    if not is_valid_ip("192.168.1.1"):
        raise Error("self-check failed: known-valid IP rejected")
    if is_valid_ip("999.1.1.1"):
        raise Error("self-check failed: known-invalid IP accepted")
    if is_valid_ip("1.2.3"):
        raise Error("self-check failed: known-invalid IP accepted")

    seed(42)
    var valid = 0
    for _ in range(n):
        var use_wide = random_si64(0, 9) >= 7
        var max_val: Int64 = 999 if use_wide else 255
        var a = random_si64(0, max_val)
        var b = random_si64(0, max_val)
        var c = random_si64(0, max_val)
        var d = random_si64(0, max_val)
        var s = String(a) + "." + String(b) + "." + String(c) + "." + String(d)
        if is_valid_ip(s):
            valid += 1

    print(valid)
