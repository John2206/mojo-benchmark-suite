import sys

BLOCK = 32


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 600

    a = [0.0] * (n * n)
    b = [0.0] * (n * n)
    for i in range(n):
        for j in range(n):
            a[i * n + j] = float((i * 3 + j) % 13)
            b[i * n + j] = float((i + j * 2) % 17)

    c = [0.0] * (n * n)
    for ii in range(0, n, BLOCK):
        i_max = min(ii + BLOCK, n)
        for kk in range(0, n, BLOCK):
            k_max = min(kk + BLOCK, n)
            for jj in range(0, n, BLOCK):
                j_max = min(jj + BLOCK, n)
                for i in range(ii, i_max):
                    for k in range(kk, k_max):
                        aik = a[i * n + k]
                        for j in range(jj, j_max):
                            c[i * n + j] += aik * b[k * n + j]

    expected = sum(a[k] * b[k * n] for k in range(n))
    assert c[0] == expected, "self-check failed: c[0][0] mismatch"

    print(f"{c[(n - 1) * n + (n - 1)]:.2f}")


if __name__ == "__main__":
    main()
