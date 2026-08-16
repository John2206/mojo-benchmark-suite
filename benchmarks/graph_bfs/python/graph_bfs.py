import random
import sys

EDGES_PER_NODE = 4


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 500_000

    random.seed(42)
    adj = [0] * (n * EDGES_PER_NODE)
    for i in range(n):
        adj[i * EDGES_PER_NODE] = (i + 1) % n
        for k in range(1, EDGES_PER_NODE):
            adj[i * EDGES_PER_NODE + k] = random.randrange(n)

    visited = [False] * n
    queue = [0] * n
    head = tail = 0
    visited[0] = True
    queue[tail] = 0
    tail += 1
    visited_count = 1

    while head < tail:
        node = queue[head]
        head += 1
        for k in range(EDGES_PER_NODE):
            nxt = adj[node * EDGES_PER_NODE + k]
            if not visited[nxt]:
                visited[nxt] = True
                visited_count += 1
                queue[tail] = nxt
                tail += 1

    assert visited_count == n, "self-check failed: not all nodes reachable"
    print(visited_count)


if __name__ == "__main__":
    main()
