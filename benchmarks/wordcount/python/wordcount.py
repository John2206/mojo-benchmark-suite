import sys

VOCAB = [
    "the", "of", "and", "a", "to", "in", "is", "you", "that", "it",
    "he", "was", "for", "on", "are", "as", "with", "his", "they", "at",
]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000

    state = 42

    def lcg_next():
        nonlocal state
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        return state

    counts = {}
    for _ in range(n):
        word = VOCAB[lcg_next() % len(VOCAB)]
        counts[word] = counts.get(word, 0) + 1

    assert sum(counts.values()) == n, "self-check failed: counts do not sum to n"
    print(len(counts))


if __name__ == "__main__":
    main()
