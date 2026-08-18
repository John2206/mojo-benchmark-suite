import sys

import cupy as cp


def main():
    _n = int(sys.argv[1]) if len(sys.argv) > 1 else 0

    buf = cp.zeros(1, dtype=cp.int32)
    del buf

    print(0)


if __name__ == "__main__":
    main()
