import sys


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 400

    a = [[(i * 3 + j) % 13 for j in range(n)] for i in range(n)]
    b = [[(i + j * 2) % 17 for j in range(n)] for i in range(n)]
    c = [[0] * n for _ in range(n)]

    for i in range(n):
        ai = a[i]
        ci = c[i]
        for k in range(n):
            aik = ai[k]
            bk = b[k]
            for j in range(n):
                ci[j] += aik * bk[j]

    expected = sum(a[0][k] * b[k][0] for k in range(n))
    assert c[0][0] == expected, "self-check failed: c[0][0] mismatch"
    print(f"{c[n - 1][n - 1]:.2f}")


if __name__ == "__main__":
    main()
