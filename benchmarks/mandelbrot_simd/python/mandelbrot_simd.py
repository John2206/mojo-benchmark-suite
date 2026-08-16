import sys

import numpy as np

MAX_ITER = 1000


def escape_iters_single(cr, ci):
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

    assert escape_iters_single(0.0, 0.0) == MAX_ITER, "self-check failed: origin should never escape"
    assert escape_iters_single(2.0, 2.0) < MAX_ITER, "self-check failed: far point should escape quickly"

    py, px = np.mgrid[0:n, 0:n]
    ci_grid = -1.5 + 3.0 * py / n
    cr_grid = -2.0 + 3.0 * px / n

    zr = np.zeros((n, n))
    zi = np.zeros((n, n))
    iters = np.zeros((n, n), dtype=np.int64)
    active = np.ones((n, n), dtype=bool)

    for _ in range(MAX_ITER):
        zr2 = zr * zr
        zi2 = zi * zi
        still = (zr2 + zi2 <= 4.0) & active
        if not still.any():
            break
        new_zi = 2.0 * zr * zi + ci_grid
        new_zr = zr2 - zi2 + cr_grid
        zr = np.where(still, new_zr, zr)
        zi = np.where(still, new_zi, zi)
        iters = np.where(still, iters + 1, iters)
        active = still

    count = int(np.sum(iters == MAX_ITER))
    print(count)


if __name__ == "__main__":
    main()
