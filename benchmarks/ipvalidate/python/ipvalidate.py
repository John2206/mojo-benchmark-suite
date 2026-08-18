import sys


def parse_group(s):
    if not s or len(s) > 3 or not s.isdigit():
        return None
    val = int(s)
    return val if val <= 255 else None


def is_valid_ip(s):
    parts = s.split(".")
    if len(parts) != 4:
        return False
    return all(parse_group(p) is not None for p in parts)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000

    assert is_valid_ip("192.168.1.1"), "self-check failed: known-valid IP rejected"
    assert not is_valid_ip("999.1.1.1"), "self-check failed: known-invalid IP accepted"
    assert not is_valid_ip("1.2.3"), "self-check failed: known-invalid IP accepted"

    state = 42

    def lcg_next():
        nonlocal state
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        return state

    valid = 0
    for _ in range(n):
        max_val = 255 if lcg_next() % 10 < 7 else 999
        a = lcg_next() % (max_val + 1)
        b = lcg_next() % (max_val + 1)
        c = lcg_next() % (max_val + 1)
        d = lcg_next() % (max_val + 1)
        s = f"{a}.{b}.{c}.{d}"
        if is_valid_ip(s):
            valid += 1

    print(valid)


if __name__ == "__main__":
    main()
