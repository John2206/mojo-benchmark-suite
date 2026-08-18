from std.sys import argv
from std.math import abs


def format2(value: Float64) -> String:
    """Matches C's "%.2f" so all five languages print the same bytes."""
    var sign = "-" if value < 0.0 else ""
    var scaled = Int(abs(value) * 100.0 + 0.5)
    var whole = scaled // 100
    var frac = scaled % 100
    var frac_str = String(frac)
    while frac_str.byte_length() < 2:
        frac_str = "0" + frac_str
    return sign + String(whole) + "." + frac_str


def main() raises:
    var args = argv()
    var n = 400
    if len(args) > 1:
        n = atol(args[1])

    var a = List[Float64](length=n * n, fill=0.0)
    var b = List[Float64](length=n * n, fill=0.0)
    for i in range(n):
        for j in range(n):
            a[i * n + j] = Float64((i * 3 + j) % 13)
            b[i * n + j] = Float64((i + j * 2) % 17)

    var c = List[Float64](length=n * n, fill=0.0)
    for i in range(n):
        for k in range(n):
            var aik = a[i * n + k]
            for j in range(n):
                c[i * n + j] += aik * b[k * n + j]

    var expected: Float64 = 0.0
    for k in range(n):
        expected += a[k] * b[k * n]
    if c[0] != expected:
        raise Error("self-check failed: c[0][0] mismatch")

    print(format2(c[(n - 1) * n + (n - 1)]))
