from std.sys import argv

comptime EDGES_PER_NODE = 4
comptime INF = 4611686018427387903


struct MinHeap(Movable):
    var heap_dist: List[Int]
    var heap_node: List[Int]
    var size: Int

    def __init__(out self, capacity: Int):
        self.heap_dist = List[Int](length=capacity, fill=0)
        self.heap_node = List[Int](length=capacity, fill=0)
        self.size = 0

    def push(mut self, dist: Int, node: Int):
        var i = self.size
        self.heap_dist[i] = dist
        self.heap_node[i] = node
        self.size += 1
        while i > 0:
            var parent = (i - 1) // 2
            if self.heap_dist[parent] <= self.heap_dist[i]:
                break
            var td = self.heap_dist[parent]
            var tn = self.heap_node[parent]
            self.heap_dist[parent] = self.heap_dist[i]
            self.heap_node[parent] = self.heap_node[i]
            self.heap_dist[i] = td
            self.heap_node[i] = tn
            i = parent

    def pop(mut self) -> Tuple[Int, Int]:
        var top_dist = self.heap_dist[0]
        var top_node = self.heap_node[0]
        self.size -= 1
        self.heap_dist[0] = self.heap_dist[self.size]
        self.heap_node[0] = self.heap_node[self.size]
        var i = 0
        while True:
            var left = 2 * i + 1
            var right = 2 * i + 2
            var smallest = i
            if left < self.size and self.heap_dist[left] < self.heap_dist[smallest]:
                smallest = left
            if right < self.size and self.heap_dist[right] < self.heap_dist[smallest]:
                smallest = right
            if smallest == i:
                break
            var td = self.heap_dist[i]
            var tn = self.heap_node[i]
            self.heap_dist[i] = self.heap_dist[smallest]
            self.heap_node[i] = self.heap_node[smallest]
            self.heap_dist[smallest] = td
            self.heap_node[smallest] = tn
            i = smallest
        return (top_dist, top_node)


def main() raises:
    var args = argv()
    var n = 300_000
    if len(args) > 1:
        n = atol(args[1])

    var adj = List[Int](length=n * EDGES_PER_NODE, fill=0)
    var w = List[Int](length=n * EDGES_PER_NODE, fill=0)
    for i in range(n):
        adj[i * EDGES_PER_NODE] = (i + 1) % n
        w[i * EDGES_PER_NODE] = (i * 3) % 20 + 1
        for k in range(1, EDGES_PER_NODE):
            adj[i * EDGES_PER_NODE + k] = (i * 7 + k * 13 + 5) % n
            w[i * EDGES_PER_NODE + k] = (i * 3 + k * 11) % 20 + 1

    var dist = List[Int](length=n, fill=INF)
    dist[0] = 0

    var heap = MinHeap(n * EDGES_PER_NODE + 1)
    heap.push(0, 0)

    while heap.size > 0:
        var top = heap.pop()
        var d = top[0]
        var u = top[1]
        if d > dist[u]:
            continue
        for k in range(EDGES_PER_NODE):
            var v = adj[u * EDGES_PER_NODE + k]
            var nd = d + w[u * EDGES_PER_NODE + k]
            if nd < dist[v]:
                dist[v] = nd
                heap.push(nd, v)

    if dist[0] != 0:
        raise Error("self-check failed: dist[0] should be 0")

    var ring_bound = 0
    var total = 0
    for i in range(n):
        if i > 0:
            ring_bound += w[(i - 1) * EDGES_PER_NODE]
        if dist[i] < 0 or dist[i] > ring_bound:
            raise Error("self-check failed: dist out of bounds")
        total += dist[i]

    print(total)
