from std.sys import argv


def main() raises:
    var args = argv()
    var n = 2_000_000
    if len(args) > 1:
        n = atol(args[1])

    var vocab = [
        "the", "of", "and", "a", "to", "in", "is", "you", "that", "it",
        "he", "was", "for", "on", "are", "as", "with", "his", "they", "at",
    ]

    var state: UInt32 = 42
    var counts = Dict[String, Int]()
    for _ in range(n):
        state = (state * UInt32(1103515245) + UInt32(12345)) & UInt32(0x7FFFFFFF)
        var idx = Int(state) % len(vocab)
        var word = vocab[idx]
        counts[word] = counts.get(word, 0) + 1

    var total = 0
    for count in counts.values():
        total += count
    if total != n:
        raise Error("self-check failed: counts do not sum to n")

    print(len(counts))
