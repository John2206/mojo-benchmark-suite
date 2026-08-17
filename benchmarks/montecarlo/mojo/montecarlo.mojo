from std.sys import argv
from std.math import sqrt

comptime PI = 3.14159265358979323846


def format6(value: Float64) -> String:
    var scaled = Int(value * 1000000.0 + 0.5)
    var whole = scaled // 1000000
    var frac = scaled % 1000000
    var frac_str = String(frac)
    while frac_str.byte_length() < 6:
        frac_str = "0" + frac_str
    return String(whole) + "." + frac_str


def main() raises:
    var args = argv()
    var n = 50_000_000
    if len(args) > 1:
        n = atol(args[1])

    var state: UInt32 = 1
    var inside = 0
    for _ in range(n):
        state = (state * UInt32(1103515245) + UInt32(12345)) & UInt32(0x7FFFFFFF)
        var x = Float64(state) / 2147483648.0
        state = (state * UInt32(1103515245) + UInt32(12345)) & UInt32(0x7FFFFFFF)
        var y = Float64(state) / 2147483648.0
        if x * x + y * y <= 1.0:
            inside += 1

    var pi_estimate = 4.0 * Float64(inside) / Float64(n)
    var tolerance = 10.0 / sqrt(Float64(n))

    if abs(pi_estimate - PI) >= tolerance:
        raise Error("self-check failed: pi estimate out of tolerance")

    print(format6(pi_estimate))
