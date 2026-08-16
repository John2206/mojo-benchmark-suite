import sys


def parse_int(s, pos):
    val = 0
    n = len(s)
    while pos[0] < n and s[pos[0]].isdigit():
        val = val * 10 + int(s[pos[0]])
        pos[0] += 1
    return val


def parse_decimal1(s, pos):
    whole = parse_int(s, pos)
    pos[0] += 1  # '.'
    frac = int(s[pos[0]])
    pos[0] += 1
    return whole + frac / 10.0


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000

    parts = ["["]
    for i in range(n):
        if i > 0:
            parts.append(",")
        parts.append(f'{{"id":{i},"name":"item{i}","value":{i * 0.5:.1f}}}')
    parts.append("]")
    json_str = "".join(parts)

    pos = [1]  # skip '['
    id_sum = 0
    decoded_count = 0
    while json_str[pos[0]] != "]":
        pos[0] += 1  # '{'
        pos[0] += len('"id":')
        id_ = parse_int(json_str, pos)
        pos[0] += len(',"name":"item')
        parse_int(json_str, pos)  # skip digits in name, not re-checked
        pos[0] += len('","value":')
        value = parse_decimal1(json_str, pos)
        pos[0] += 1  # '}'
        if pos[0] < len(json_str) and json_str[pos[0]] == ",":
            pos[0] += 1

        assert value == id_ * 0.5, f"self-check failed: decoded value mismatch for id {id_}"
        id_sum += id_
        decoded_count += 1

    expected_sum = n * (n - 1) // 2
    assert id_sum == expected_sum and decoded_count == n, "self-check failed: id sum or count mismatch"
    print(id_sum)


if __name__ == "__main__":
    main()
