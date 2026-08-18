from std.sys import argv


def main() raises:
    var args = argv()
    var n = 0
    if len(args) > 1:
        n = atol(args[1])
    _ = n
    print(0)
