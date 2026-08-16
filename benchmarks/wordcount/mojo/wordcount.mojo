from std.sys import argv
from std.random import random_si64, seed


def main() raises:
    var args = argv()
    var n = 2_000_000
    if len(args) > 1:
        n = atol(args[1])

    var vocab = [
        "the", "of", "and", "a", "to", "in", "is", "you", "that", "it",
        "he", "was", "for", "on", "are", "as", "with", "his", "they", "at",
    ]

    seed(42)
    var counts = Dict[String, Int]()
    for _ in range(n):
        var idx = Int(random_si64(0, Int64(len(vocab) - 1)))
        var word = vocab[idx]
        counts[word] = counts.get(word, 0) + 1

    var total = 0
    for count in counts.values():
        total += count
    if total != n:
        raise Error("self-check failed: counts do not sum to n")

    print(len(counts))
