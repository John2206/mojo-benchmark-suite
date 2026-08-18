from std.sys import argv
from std.memory import alloc


struct Node:
    comptime NodePointer = UnsafePointer[Self, MutUntrackedOrigin]

    var val: Int64
    var left: Optional[Self.NodePointer]
    var right: Optional[Self.NodePointer]

    def __init__(out self, val: Int64):
        self.val = val
        self.left = None
        self.right = None

    @staticmethod
    def make_node(val: Int64) -> Self.NodePointer:
        var node_ptr = alloc[Self](1)
        node_ptr.unsafe_write(Self(val))
        return node_ptr


def insert(root: Node.NodePointer, val: Int64):
    var cur = root
    while True:
        if val < cur[].val:
            if cur[].left:
                cur = cur[].left.value()
            else:
                cur[].left = Node.make_node(val)
                return
        else:
            if cur[].right:
                cur = cur[].right.value()
            else:
                cur[].right = Node.make_node(val)
                return


def main() raises:
    var args = argv()
    var n = 300_000
    if len(args) > 1:
        n = atol(args[1])

    var state: UInt32 = 42

    var root = Node.make_node(0)
    state = (state * UInt32(1103515245) + UInt32(12345)) & UInt32(0x7FFFFFFF)
    root[].val = Int64(state)
    for _ in range(1, n):
        state = (state * UInt32(1103515245) + UInt32(12345)) & UInt32(0x7FFFFFFF)
        insert(root, Int64(state))

    var prev: Int64 = 0
    var first = True
    var ok = True
    var max_val: Int64 = 0
    var count = 0

    var stack = List[Node.NodePointer]()
    var node: Optional[Node.NodePointer] = root
    while len(stack) > 0 or node:
        while node:
            stack.append(node.value())
            node = node.value()[].left
        var cur = stack.pop()
        if not first and cur[].val < prev:
            ok = False
        first = False
        prev = cur[].val
        max_val = cur[].val
        count += 1
        node = cur[].right

    if not ok or count != n:
        raise Error("self-check failed: in-order traversal not sorted or count mismatch")

    print(max_val)
