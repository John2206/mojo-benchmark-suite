from std.sys import argv

comptime BLOCK = 32


def main() raises:
    var args = argv()
    var n = 600
    if len(args) > 1:
        n = atol(args[1])

    var a = List[Float64](length=n * n, fill=0.0)
    var b = List[Float64](length=n * n, fill=0.0)
    for i in range(n):
        for j in range(n):
            a[i * n + j] = Float64((i * 3 + j) % 13)
            b[i * n + j] = Float64((i + j * 2) % 17)

    var c = List[Float64](length=n * n, fill=0.0)
    var ii = 0
    while ii < n:
        var i_max = ii + BLOCK
        if i_max > n:
            i_max = n
        var kk = 0
        while kk < n:
            var k_max = kk + BLOCK
            if k_max > n:
                k_max = n
            var jj = 0
            while jj < n:
                var j_max = jj + BLOCK
                if j_max > n:
                    j_max = n
                for i in range(ii, i_max):
                    for k in range(kk, k_max):
                        var aik = a[i * n + k]
                        for j in range(jj, j_max):
                            c[i * n + j] += aik * b[k * n + j]
                jj += BLOCK
            kk += BLOCK
        ii += BLOCK

    var expected: Float64 = 0.0
    for k in range(n):
        expected += a[k] * b[k * n]
    if c[0] != expected:
        raise Error("self-check failed: c[0][0] mismatch")

    print(c[(n - 1) * n + (n - 1)])
