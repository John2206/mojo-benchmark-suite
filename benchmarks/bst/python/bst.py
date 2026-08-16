import random
import sys


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def insert(root, val):
    cur = root
    while True:
        if val < cur.val:
            if cur.left is None:
                cur.left = Node(val)
                return
            cur = cur.left
        else:
            if cur.right is None:
                cur.right = Node(val)
                return
            cur = cur.right


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300_000

    random.seed(42)
    root = Node(random.getrandbits(31))
    for _ in range(n - 1):
        insert(root, random.getrandbits(31))

    prev = None
    ok = True
    count = 0
    max_val = None
    stack = []
    node = root
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack.pop()
        if prev is not None and node.val < prev:
            ok = False
        prev = node.val
        max_val = node.val
        count += 1
        node = node.right

    assert ok and count == n, "self-check failed: in-order traversal not sorted or count mismatch"
    print(max_val)


if __name__ == "__main__":
    main()
