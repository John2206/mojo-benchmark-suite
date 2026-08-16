import random
import sys


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
    random.seed(42)
    arr = [random.randint(-(2**31), 2**31 - 1) for _ in range(n)]

    arr.sort()

    assert all(arr[i - 1] <= arr[i] for i in range(1, n)), "self-check failed: array not sorted"
    print(arr[-1])


if __name__ == "__main__":
    main()
