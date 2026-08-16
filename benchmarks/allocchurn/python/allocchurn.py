import sys


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5_000_000

    total = 0
    for _ in range(n):
        arr = list(range(64))
        total += sum(arr)

    assert total == n * 2016, "self-check failed: total mismatch"
    print(total)


if __name__ == "__main__":
    main()
