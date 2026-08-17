import sys

PI = 3.14159265358979323846


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50_000_000

    state = 1
    inside = 0
    for _ in range(n):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        x = state / 2147483648.0
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        y = state / 2147483648.0
        if x * x + y * y <= 1.0:
            inside += 1

    pi_estimate = 4.0 * inside / n
    tolerance = 10.0 / n**0.5

    assert abs(pi_estimate - PI) < tolerance, f"self-check failed: pi estimate out of tolerance: {pi_estimate}"

    print(f"{pi_estimate:.6f}")


if __name__ == "__main__":
    main()
