import sys

MAX_ITER = 1000


def escape_iters(cr, ci):
    zr = zi = 0.0
    i = 0
    while i < MAX_ITER:
        zr2, zi2 = zr * zr, zi * zi
        if zr2 + zi2 > 4.0:
            break
        zi = 2.0 * zr * zi + ci
        zr = zr2 - zi2 + cr
        i += 1
    return i


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 800

    assert escape_iters(0.0, 0.0) == MAX_ITER, "self-check failed: origin should never escape"
    assert escape_iters(2.0, 2.0) < MAX_ITER, "self-check failed: far point should escape quickly"

    count = 0
    for py in range(n):
        ci = -1.5 + 3.0 * py / n
        for px in range(n):
            cr = -2.0 + 3.0 * px / n
            if escape_iters(cr, ci) == MAX_ITER:
                count += 1
    print(count)


if __name__ == "__main__":
    main()
