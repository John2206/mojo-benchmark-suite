from std.sys import argv


def main() raises:
    var args = argv()
    var n = 2_000_000
    if len(args) > 1:
        n = atol(args[1])

    var state: UInt32 = 42
    var data = List[Int64](length=n, fill=Int64(0))
    for i in range(n):
        state = (state * UInt32(1103515245) + UInt32(12345)) & UInt32(0x7FFFFFFF)
        data[i] = Int64(state)

    sort(data)

    for i in range(1, n):
        if data[i - 1] > data[i]:
            raise Error("self-check failed: array not sorted")

    print(data[n - 1])
