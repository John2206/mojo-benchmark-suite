import random
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

    random.seed(42)
    valid = 0
    for _ in range(n):
        max_val = 255 if random.random() < 0.7 else 999
        a, b, c, d = (random.randint(0, max_val) for _ in range(4))
        s = f"{a}.{b}.{c}.{d}"
        if is_valid_ip(s):
            valid += 1

    print(valid)


if __name__ == "__main__":
    main()
