import sys


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000

    state = 42
    arr = [0] * n
    for i in range(n):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        arr[i] = state

    arr.sort()

    assert all(arr[i - 1] <= arr[i] for i in range(1, n)), "self-check failed: array not sorted"
    print(arr[-1])


if __name__ == "__main__":
    main()
