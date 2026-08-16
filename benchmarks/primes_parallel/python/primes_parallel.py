import sys
from multiprocessing import Pool

NUM_THREADS = 4


def is_prime(x):
    if x < 2:
        return False
    if x % 2 == 0:
        return x == 2
    d = 3
    while d * d <= x:
        if x % d == 0:
            return False
        d += 2
    return True


def count_range(bounds):
    start, end = bounds
    return sum(1 for x in range(start, end) if is_prime(x))


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000

    assert is_prime(2) and is_prime(97) and not is_prime(100) and not is_prime(1), \
        "self-check failed: is_prime disagrees with known facts"

    chunk = n // NUM_THREADS
    ranges = []
    for i in range(NUM_THREADS):
        start = max(i * chunk, 2)
        end = n if i == NUM_THREADS - 1 else (i + 1) * chunk
        ranges.append((start, end))

    with Pool(NUM_THREADS) as pool:
        total = sum(pool.map(count_range, ranges))

    print(total)


if __name__ == "__main__":
    main()
