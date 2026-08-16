import sys


def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    assert fib(10) == 55, "self-check failed: fib(10) != 55"
    print(fib(n))


if __name__ == "__main__":
    main()
