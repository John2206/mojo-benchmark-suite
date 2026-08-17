import java.util.PriorityQueue;

public class Dijkstra {
    static final int EDGES_PER_NODE = 4;

    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 300_000;

        int[] adj = new int[n * EDGES_PER_NODE];
        long[] w = new long[n * EDGES_PER_NODE];
        for (int i = 0; i < n; i++) {
            adj[i * EDGES_PER_NODE] = (i + 1) % n;
            w[i * EDGES_PER_NODE] = ((long) (i * 3) % 20) + 1;
            for (int k = 1; k < EDGES_PER_NODE; k++) {
                adj[i * EDGES_PER_NODE + k] = (int) (((long) i * 7 + k * 13 + 5) % n);
                w[i * EDGES_PER_NODE + k] = (((long) i * 3 + k * 11) % 20) + 1;
            }
        }

        long inf = Long.MAX_VALUE / 2;
        long[] dist = new long[n];
        java.util.Arrays.fill(dist, inf);
        dist[0] = 0;

        PriorityQueue<long[]> heap = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
        heap.add(new long[] {0, 0});

        while (!heap.isEmpty()) {
            long[] top = heap.poll();
            long d = top[0];
            int u = (int) top[1];
            if (d > dist[u]) continue;
            for (int k = 0; k < EDGES_PER_NODE; k++) {
                int v = adj[u * EDGES_PER_NODE + k];
                long nd = d + w[u * EDGES_PER_NODE + k];
                if (nd < dist[v]) {
                    dist[v] = nd;
                    heap.add(new long[] {nd, v});
                }
            }
        }

        if (dist[0] != 0) {
            System.err.println("self-check failed: dist[0] should be 0");
            System.exit(1);
        }
        long ringBound = 0;
        long total = 0;
        for (int i = 0; i < n; i++) {
            if (i > 0) {
                ringBound += w[(i - 1) * EDGES_PER_NODE];
            }
            if (dist[i] < 0 || dist[i] > ringBound) {
                System.err.println("self-check failed: dist[" + i + "] out of bounds");
                System.exit(1);
            }
            total += dist[i];
        }

        System.out.println(total);
    }
}
