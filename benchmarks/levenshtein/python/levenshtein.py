import sys


def edit_distance(s1, s2):
    len1, len2 = len(s1), len(s2)
    prev = list(range(len2 + 1))
    cur = [0] * (len2 + 1)

    for i in range(1, len1 + 1):
        cur[0] = i
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        prev, cur = cur, prev

    return prev[len2]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5000

    assert edit_distance("kitten", "sitting") == 3, "self-check failed: edit_distance(kitten,sitting) mismatch"

    alphabet = "ACGT"
    s1 = []
    s2 = []
    for i in range(n):
        base = (i * 7 + 3) % 4
        s1.append(alphabet[base])
        s2.append(alphabet[(base + 1) % 4] if i % 5 == 4 else alphabet[base])

    print(edit_distance(s1, s2))


if __name__ == "__main__":
    main()
