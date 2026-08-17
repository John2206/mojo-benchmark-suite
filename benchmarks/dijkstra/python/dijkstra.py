import heapq
import sys

EDGES_PER_NODE = 4


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300_000

    adj = [0] * (n * EDGES_PER_NODE)
    w = [0] * (n * EDGES_PER_NODE)
    for i in range(n):
        adj[i * EDGES_PER_NODE] = (i + 1) % n
        w[i * EDGES_PER_NODE] = (i * 3) % 20 + 1
        for k in range(1, EDGES_PER_NODE):
            adj[i * EDGES_PER_NODE + k] = (i * 7 + k * 13 + 5) % n
            w[i * EDGES_PER_NODE + k] = (i * 3 + k * 11) % 20 + 1

    inf = float("inf")
    dist = [inf] * n
    dist[0] = 0

    heap = [(0, 0)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for k in range(EDGES_PER_NODE):
            v = adj[u * EDGES_PER_NODE + k]
            nd = d + w[u * EDGES_PER_NODE + k]
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))

    assert dist[0] == 0, "self-check failed: dist[0] should be 0"
    ring_bound = 0
    total = 0
    for i in range(n):
        if i > 0:
            ring_bound += w[(i - 1) * EDGES_PER_NODE]
        assert 0 <= dist[i] <= ring_bound, f"self-check failed: dist[{i}] out of bounds"
        total += dist[i]

    print(total)


if __name__ == "__main__":
    main()
