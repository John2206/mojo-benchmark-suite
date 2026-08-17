from std.sys import argv

comptime WINDOW = 4096
comptime MAX_MATCH = 255
comptime MIN_MATCH = 3
comptime HASH_SIZE = 8192


def hash3(data: List[UInt8], i: Int) -> Int:
    var a = Int(data[i])
    var b = Int(data[i + 1])
    var c = Int(data[i + 2])
    return ((a * 131 + b) * 131 + c) & (HASH_SIZE - 1)


struct EncodeResult(Movable):
    var is_match: List[Bool]
    var offsets: List[Int]
    var lengths: List[Int]
    var literals: List[UInt8]

    def __init__(out self, var is_match: List[Bool], var offsets: List[Int], var lengths: List[Int], var literals: List[UInt8]):
        self.is_match = is_match^
        self.offsets = offsets^
        self.lengths = lengths^
        self.literals = literals^


def lz77_encode(data: List[UInt8]) -> EncodeResult:
    var n = len(data)
    var hash_table = List[Int](length=HASH_SIZE, fill=-1)

    var is_match = List[Bool]()
    var offsets = List[Int]()
    var lengths = List[Int]()
    var literals = List[UInt8]()

    var i = 0
    while i < n:
        var best_len = 0
        var best_cand = -1
        if i + 3 <= n:
            var h = hash3(data, i)
            var cand = hash_table[h]
            if cand != -1 and i - cand <= WINDOW:
                var match_len = 0
                while match_len < MAX_MATCH and i + match_len < n and data[cand + match_len] == data[i + match_len]:
                    match_len += 1
                if match_len >= MIN_MATCH:
                    best_len = match_len
                    best_cand = cand
            hash_table[h] = i
        if best_len >= MIN_MATCH:
            is_match.append(True)
            offsets.append(i - best_cand)
            lengths.append(best_len)
            literals.append(UInt8(0))
            i += best_len
        else:
            is_match.append(False)
            offsets.append(0)
            lengths.append(0)
            literals.append(data[i])
            i += 1

    return EncodeResult(is_match^, offsets^, lengths^, literals^)


def lz77_decode(is_match: List[Bool], offsets: List[Int], lengths: List[Int], literals: List[UInt8]) -> List[UInt8]:
    var out = List[UInt8]()
    for t in range(len(is_match)):
        if is_match[t]:
            var start = len(out) - offsets[t]
            for k in range(lengths[t]):
                out.append(out[start + k])
        else:
            out.append(literals[t])
    return out^


def main() raises:
    var args = argv()
    var n = 5_000_000
    if len(args) > 1:
        n = atol(args[1])

    var pattern = List[UInt8](length=64, fill=UInt8(0))
    for i in range(64):
        pattern[i] = UInt8((i * 7 + 3) % 251)

    var data = List[UInt8](length=n, fill=UInt8(0))
    for i in range(n):
        var v = pattern[i % 64]
        if i % 97 == 0:
            v = UInt8((Int(v) + 1) % 256)
        data[i] = v

    var result = lz77_encode(data)

    var decoded = lz77_decode(result.is_match, result.offsets, result.lengths, result.literals)

    if len(decoded) != n:
        raise Error("self-check failed: roundtrip length mismatch")
    for i in range(n):
        if decoded[i] != data[i]:
            raise Error("self-check failed: roundtrip byte mismatch")

    var compressed_bytes = 0
    for t in range(len(result.is_match)):
        if result.is_match[t]:
            compressed_bytes += 4
        else:
            compressed_bytes += 2

    print(compressed_bytes)
