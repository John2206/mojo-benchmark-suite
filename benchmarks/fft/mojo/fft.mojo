from std.sys import argv
from std.math import cos, sin, pi


def next_pow2(n: Int) -> Int:
    var p = 1
    while p < n:
        p <<= 1
    return p


def fft(mut re: List[Float64], mut im: List[Float64], invert: Bool):
    var n = len(re)
    var j = 0
    for i in range(1, n):
        var bit = n >> 1
        while (j & bit) != 0:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            var tr = re[i]
            re[i] = re[j]
            re[j] = tr
            var ti = im[i]
            im[i] = im[j]
            im[j] = ti

    var length = 2
    while length <= n:
        var sign = 1.0
        if not invert:
            sign = -1.0
        var ang = 2.0 * pi / Float64(length) * sign
        var wlen_re = cos(ang)
        var wlen_im = sin(ang)
        var i = 0
        while i < n:
            var w_re = 1.0
            var w_im = 0.0
            for k in range(i, i + length // 2):
                var u_re = re[k]
                var u_im = im[k]
                var v_re = re[k + length // 2] * w_re - im[k + length // 2] * w_im
                var v_im = re[k + length // 2] * w_im + im[k + length // 2] * w_re
                re[k] = u_re + v_re
                im[k] = u_im + v_im
                re[k + length // 2] = u_re - v_re
                im[k + length // 2] = u_im - v_im
                var nw_re = w_re * wlen_re - w_im * wlen_im
                var nw_im = w_re * wlen_im + w_im * wlen_re
                w_re = nw_re
                w_im = nw_im
            i += length
        length <<= 1

    if invert:
        for i in range(n):
            re[i] /= Float64(n)
            im[i] /= Float64(n)


def main() raises:
    var args = argv()
    var requested = 1_048_576
    if len(args) > 1:
        requested = atol(args[1])
    var n = next_pow2(requested)

    var re = List[Float64](length=n, fill=0.0)
    var im = List[Float64](length=n, fill=0.0)
    var orig = List[Float64](length=n, fill=0.0)
    for i in range(n):
        var v = Float64(i % 7) - 3.0
        re[i] = v
        orig[i] = v

    fft(re, im, False)
    fft(re, im, True)

    var max_err = 0.0
    for i in range(n):
        var err = abs(re[i] - orig[i])
        var im_err = abs(im[i])
        if im_err > err:
            err = im_err
        if err > max_err:
            max_err = err

    if max_err >= 1e-6:
        raise Error("self-check failed: roundtrip reconstruction error too large")

    print(max_err)
