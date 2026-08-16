from std.sys import argv

comptime MAX_ITER = 1000
comptime W = 4  # ponytail: fixed lane width, not simd_width_of()-detected; simplest thing that's still real SIMD


def escape_counts_row(cr_vec: SIMD[DType.float64, W], ci: Float64) -> SIMD[DType.int64, W]:
    var zr = SIMD[DType.float64, W](0.0)
    var zi = SIMD[DType.float64, W](0.0)
    var iters = SIMD[DType.int64, W](0)
    var active = SIMD[DType.bool, W](fill=True)
    var ci_vec = SIMD[DType.float64, W](ci)

    for _ in range(MAX_ITER):
        var zr2 = zr * zr
        var zi2 = zi * zi
        var still = (zr2 + zi2).le(SIMD[DType.float64, W](4.0)) & active
        if not still.reduce_or():
            break
        var new_zi = 2.0 * zr * zi + ci_vec
        var new_zr = zr2 - zi2 + cr_vec
        zr = still.select(new_zr, zr)
        zi = still.select(new_zi, zi)
        iters = still.select(iters + 1, iters)
        active = still

    return iters


def main() raises:
    var args = argv()
    var n = 800
    if len(args) > 1:
        n = atol(args[1])

    var origin_check = escape_counts_row(SIMD[DType.float64, W](0.0), 0.0)
    for lane in range(W):
        if Int(origin_check[lane]) != MAX_ITER:
            raise Error("self-check failed: origin should never escape")

    var far_check = escape_counts_row(SIMD[DType.float64, W](2.0), 2.0)
    for lane in range(W):
        if Int(far_check[lane]) >= MAX_ITER:
            raise Error("self-check failed: far point should escape quickly")

    var groups = n // W  # remainder columns (n % W) are dropped for simplicity
    var count = 0
    for py in range(n):
        var ci = -1.5 + 3.0 * Float64(py) / Float64(n)
        for gx in range(groups):
            var cr_vec = SIMD[DType.float64, W](0.0)
            for lane in range(W):
                var px = gx * W + lane
                cr_vec[lane] = -2.0 + 3.0 * Float64(px) / Float64(n)
            var iters = escape_counts_row(cr_vec, ci)
            for lane in range(W):
                if Int(iters[lane]) == MAX_ITER:
                    count += 1

    print(count)
