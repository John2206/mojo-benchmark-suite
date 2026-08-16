from std.sys import argv
from std.random import random_si64, seed

comptime EDGES_PER_NODE = 4


def main() raises:
    var args = argv()
    var n = 500_000
    if len(args) > 1:
        n = atol(args[1])

    var adj = List[Int](length=n * EDGES_PER_NODE, fill=0)
    seed(42)
    for i in range(n):
        adj[i * EDGES_PER_NODE] = (i + 1) % n
        for k in range(1, EDGES_PER_NODE):
            adj[i * EDGES_PER_NODE + k] = Int(random_si64(0, Int64(n - 1)))

    var visited = List[Bool](length=n, fill=False)
    var queue = List[Int](length=n, fill=0)
    var head = 0
    var tail = 0
    visited[0] = True
    queue[tail] = 0
    tail += 1
    var visited_count = 1

    while head < tail:
        var node = queue[head]
        head += 1
        for k in range(EDGES_PER_NODE):
            var nxt = adj[node * EDGES_PER_NODE + k]
            if not visited[nxt]:
                visited[nxt] = True
                visited_count += 1
                queue[tail] = nxt
                tail += 1

    if visited_count != n:
        raise Error("self-check failed: not all nodes reachable")

    print(visited_count)
