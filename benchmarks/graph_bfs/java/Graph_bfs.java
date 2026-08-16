import java.util.Random;

public class Graph_bfs {
    static final int EDGES_PER_NODE = 4;

    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 500_000;

        int[] adj = new int[n * EDGES_PER_NODE];
        Random rnd = new Random(42);
        for (int i = 0; i < n; i++) {
            adj[i * EDGES_PER_NODE] = (i + 1) % n;
            for (int k = 1; k < EDGES_PER_NODE; k++) {
                adj[i * EDGES_PER_NODE + k] = rnd.nextInt(n);
            }
        }

        boolean[] visited = new boolean[n];
        int[] queue = new int[n];
        int head = 0, tail = 0;
        visited[0] = true;
        queue[tail++] = 0;
        int visitedCount = 1;

        while (head < tail) {
            int node = queue[head++];
            for (int k = 0; k < EDGES_PER_NODE; k++) {
                int nxt = adj[node * EDGES_PER_NODE + k];
                if (!visited[nxt]) {
                    visited[nxt] = true;
                    visitedCount++;
                    queue[tail++] = nxt;
                }
            }
        }

        if (visitedCount != n) {
            System.err.println("self-check failed: not all nodes reachable");
            System.exit(1);
        }

        System.out.println(visitedCount);
    }
}
