#include <stdio.h>
#include <stdlib.h>

#define EDGES_PER_NODE 4
#define LONG_INF 0x3f3f3f3f3f3f3f3fL

typedef struct {
    long dist;
    long node;
} HeapItem;

static HeapItem *heap;
static long heap_size;

static void heap_push(long dist, long node) {
    long i = heap_size++;
    heap[i].dist = dist;
    heap[i].node = node;
    while (i > 0) {
        long parent = (i - 1) / 2;
        if (heap[parent].dist <= heap[i].dist) break;
        HeapItem tmp = heap[parent]; heap[parent] = heap[i]; heap[i] = tmp;
        i = parent;
    }
}

static HeapItem heap_pop(void) {
    HeapItem top = heap[0];
    heap_size--;
    heap[0] = heap[heap_size];
    long i = 0;
    while (1) {
        long left = 2 * i + 1, right = 2 * i + 2, smallest = i;
        if (left < heap_size && heap[left].dist < heap[smallest].dist) smallest = left;
        if (right < heap_size && heap[right].dist < heap[smallest].dist) smallest = right;
        if (smallest == i) break;
        HeapItem tmp = heap[i]; heap[i] = heap[smallest]; heap[smallest] = tmp;
        i = smallest;
    }
    return top;
}

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 300000;

    long *adj = malloc((size_t)n * EDGES_PER_NODE * sizeof(long));
    long *w = malloc((size_t)n * EDGES_PER_NODE * sizeof(long));
    for (long i = 0; i < n; i++) {
        adj[i * EDGES_PER_NODE] = (i + 1) % n;
        w[i * EDGES_PER_NODE] = ((i * 3) % 20) + 1;
        for (int k = 1; k < EDGES_PER_NODE; k++) {
            adj[i * EDGES_PER_NODE + k] = (i * 7 + k * 13 + 5) % n;
            w[i * EDGES_PER_NODE + k] = ((i * 3 + k * 11) % 20) + 1;
        }
    }

    long *dist = malloc((size_t)n * sizeof(long));
    for (long i = 0; i < n; i++) dist[i] = LONG_INF;
    dist[0] = 0;

    heap = malloc((size_t)(n * EDGES_PER_NODE + 1) * sizeof(HeapItem));
    heap_size = 0;
    heap_push(0, 0);

    while (heap_size > 0) {
        HeapItem top = heap_pop();
        long d = top.dist, u = top.node;
        if (d > dist[u]) continue;
        for (int k = 0; k < EDGES_PER_NODE; k++) {
            long v = adj[u * EDGES_PER_NODE + k];
            long nd = d + w[u * EDGES_PER_NODE + k];
            if (nd < dist[v]) {
                dist[v] = nd;
                heap_push(nd, v);
            }
        }
    }

    if (dist[0] != 0) {
        fprintf(stderr, "self-check failed: dist[0] should be 0\n");
        return 1;
    }
    long ring_bound = 0;
    long total = 0;
    for (long i = 0; i < n; i++) {
        if (i > 0) {
            ring_bound += w[(i - 1) * EDGES_PER_NODE];
        }
        if (dist[i] < 0 || dist[i] > ring_bound) {
            fprintf(stderr, "self-check failed: dist[%ld] out of bounds\n", i);
            return 1;
        }
        total += dist[i];
    }

    printf("%ld\n", total);

    free(adj);
    free(w);
    free(dist);
    free(heap);
    return 0;
}
