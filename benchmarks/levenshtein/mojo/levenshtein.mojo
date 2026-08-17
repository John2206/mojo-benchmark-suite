from std.sys import argv


def str_bytes(s: String) -> List[UInt8]:
    var out = List[UInt8]()
    for b in s.as_bytes():
        out.append(b)
    return out^


def edit_distance(s1: List[UInt8], s2: List[UInt8]) -> Int:
    var len1 = len(s1)
    var len2 = len(s2)
    var prev = List[Int](length=len2 + 1, fill=0)
    var cur = List[Int](length=len2 + 1, fill=0)
    for j in range(len2 + 1):
        prev[j] = j

    for i in range(1, len1 + 1):
        cur[0] = i
        for j in range(1, len2 + 1):
            var cost = 0
            if s1[i - 1] != s2[j - 1]:
                cost = 1
            var deletion = prev[j] + 1
            var ins = cur[j - 1] + 1
            var sub = prev[j - 1] + cost
            var m = deletion
            if ins < m:
                m = ins
            if sub < m:
                m = sub
            cur[j] = m
        var tmp = prev^
        prev = cur^
        cur = tmp^

    return prev[len2]


def main() raises:
    var args = argv()
    var n = 5000
    if len(args) > 1:
        n = atol(args[1])

    if edit_distance(str_bytes("kitten"), str_bytes("sitting")) != 3:
        raise Error("self-check failed: edit_distance(kitten,sitting) mismatch")

    var alphabet = str_bytes("ACGT")
    var s1 = List[UInt8](length=n, fill=UInt8(0))
    var s2 = List[UInt8](length=n, fill=UInt8(0))
    for i in range(n):
        var base = (i * 7 + 3) % 4
        s1[i] = alphabet[base]
        if i % 5 == 4:
            s2[i] = alphabet[(base + 1) % 4]
        else:
            s2[i] = alphabet[base]

    print(edit_distance(s1, s2))
