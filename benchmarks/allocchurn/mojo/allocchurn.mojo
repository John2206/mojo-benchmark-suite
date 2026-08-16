from std.sys import argv


def main() raises:
    var args = argv()
    var n = 5_000_000
    if len(args) > 1:
        n = atol(args[1])

    var total: Int = 0
    for _ in range(n):
        var arr = List[Int](length=64, fill=0)
        for j in range(64):
            arr[j] = j
        var s = 0
        for j in range(64):
            s += arr[j]
        total += s

    if total != n * 2016:
        raise Error("self-check failed: total mismatch")

    print(total)
