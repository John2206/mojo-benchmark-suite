#include <stdio.h>
#include <stdlib.h>

#define EDGES_PER_NODE 4

static unsigned int lcg_state;

static long lcg_next(void) {
    lcg_state = (lcg_state * 1103515245u + 12345u) & 0x7fffffffu;
    return (long)lcg_state;
}

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 500000;

    int *adj = malloc((size_t)n * EDGES_PER_NODE * sizeof(int));
    lcg_state = 42;
    for (long i = 0; i < n; i++) {
        adj[i * EDGES_PER_NODE] = (int)((i + 1) % n);
        for (int k = 1; k < EDGES_PER_NODE; k++) {
            adj[i * EDGES_PER_NODE + k] = (int)(lcg_next() % n);
        }
    }

    char *visited = calloc((size_t)n, 1);
    long *queue = malloc((size_t)n * sizeof(long));
    long head = 0, tail = 0;
    visited[0] = 1;
    queue[tail++] = 0;
    long visited_count = 1;

    while (head < tail) {
        long node = queue[head++];
        for (int k = 0; k < EDGES_PER_NODE; k++) {
            long nxt = adj[node * EDGES_PER_NODE + k];
            if (!visited[nxt]) {
                visited[nxt] = 1;
                visited_count++;
                queue[tail++] = nxt;
            }
        }
    }

    if (visited_count != n) {
        fprintf(stderr, "self-check failed: not all nodes reachable (%ld/%ld)\n", visited_count, n);
        return 1;
    }

    printf("%ld\n", visited_count);
    free(adj);
    free(visited);
    free(queue);
    return 0;
}
