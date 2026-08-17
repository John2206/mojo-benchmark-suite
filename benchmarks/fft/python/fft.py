import math
import sys


def next_pow2(n):
    p = 1
    while p < n:
        p <<= 1
    return p


def fft(re, im, invert):
    n = len(re)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            re[i], re[j] = re[j], re[i]
            im[i], im[j] = im[j], im[i]

    length = 2
    while length <= n:
        ang = 2.0 * math.pi / length * (1.0 if invert else -1.0)
        wlen_re = math.cos(ang)
        wlen_im = math.sin(ang)
        for i in range(0, n, length):
            w_re, w_im = 1.0, 0.0
            for k in range(i, i + length // 2):
                u_re, u_im = re[k], im[k]
                v_re = re[k + length // 2] * w_re - im[k + length // 2] * w_im
                v_im = re[k + length // 2] * w_im + im[k + length // 2] * w_re
                re[k] = u_re + v_re
                im[k] = u_im + v_im
                re[k + length // 2] = u_re - v_re
                im[k + length // 2] = u_im - v_im
                w_re, w_im = w_re * wlen_re - w_im * wlen_im, w_re * wlen_im + w_im * wlen_re
        length <<= 1

    if invert:
        for i in range(n):
            re[i] /= n
            im[i] /= n


def main():
    requested = int(sys.argv[1]) if len(sys.argv) > 1 else 1_048_576
    n = next_pow2(requested)

    re = [(i % 7) - 3.0 for i in range(n)]
    im = [0.0] * n
    orig = list(re)

    fft(re, im, False)
    fft(re, im, True)

    max_err = 0.0
    for i in range(n):
        err = max(abs(re[i] - orig[i]), abs(im[i]))
        if err > max_err:
            max_err = err

    assert max_err < 1e-6, f"self-check failed: roundtrip reconstruction error too large: {max_err}"

    print(f"{max_err:e}")


if __name__ == "__main__":
    main()
