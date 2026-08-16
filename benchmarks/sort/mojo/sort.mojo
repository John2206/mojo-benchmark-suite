from std.random import randint, seed
from std.sys import argv


def main() raises:
    var args = argv()
    var n = 2_000_000
    if len(args) > 1:
        n = atol(args[1])

    seed(42)
    var data = List(length=n, fill=Int32(0))
    randint(data, -1_000_000_000, 1_000_000_000)

    sort(data)

    for i in range(1, n):
        if data[i - 1] > data[i]:
            raise Error("self-check failed: array not sorted")

    print(data[n - 1])
