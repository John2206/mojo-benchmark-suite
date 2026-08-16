from std.sys import argv

comptime MAX_ITER = 1000


def escape_iters(cr: Float64, ci: Float64) -> Int:
    var zr: Float64 = 0.0
    var zi: Float64 = 0.0
    var i = 0
    while i < MAX_ITER:
        var zr2 = zr * zr
        var zi2 = zi * zi
        if zr2 + zi2 > 4.0:
            break
        var new_zi = 2.0 * zr * zi + ci
        zr = zr2 - zi2 + cr
        zi = new_zi
        i += 1
    return i


def main() raises:
    var args = argv()
    var n = 800
    if len(args) > 1:
        n = atol(args[1])

    if escape_iters(0.0, 0.0) != MAX_ITER:
        raise Error("self-check failed: origin should never escape")
    if escape_iters(2.0, 2.0) >= MAX_ITER:
        raise Error("self-check failed: far point should escape quickly")

    var count = 0
    for py in range(n):
        var ci = -1.5 + 3.0 * Float64(py) / Float64(n)
        for px in range(n):
            var cr = -2.0 + 3.0 * Float64(px) / Float64(n)
            if escape_iters(cr, ci) == MAX_ITER:
                count += 1
    print(count)
