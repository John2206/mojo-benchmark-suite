from std.sys import argv


def fib(n: Int) -> Int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def main() raises:
    var args = argv()
    var n = 32
    if len(args) > 1:
        n = atol(args[1])
    if fib(10) != 55:
        raise Error("self-check failed: fib(10) != 55")
    print(fib(n))
