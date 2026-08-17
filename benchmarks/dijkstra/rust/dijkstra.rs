use std::cmp::Reverse;
use std::collections::BinaryHeap;
use std::env;

const EDGES_PER_NODE: usize = 4;

fn main() {
    let n: usize = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(300_000);

    let mut adj = vec![0usize; n * EDGES_PER_NODE];
    let mut w = vec![0i64; n * EDGES_PER_NODE];
    for i in 0..n {
        adj[i * EDGES_PER_NODE] = (i + 1) % n;
        w[i * EDGES_PER_NODE] = ((i * 3) % 20) as i64 + 1;
        for k in 1..EDGES_PER_NODE {
            adj[i * EDGES_PER_NODE + k] = (i * 7 + k * 13 + 5) % n;
            w[i * EDGES_PER_NODE + k] = ((i * 3 + k * 11) % 20) as i64 + 1;
        }
    }

    let inf = i64::MAX / 2;
    let mut dist = vec![inf; n];
    dist[0] = 0;

    let mut heap: BinaryHeap<Reverse<(i64, usize)>> = BinaryHeap::new();
    heap.push(Reverse((0, 0)));

    while let Some(Reverse((d, u))) = heap.pop() {
        if d > dist[u] {
            continue;
        }
        for k in 0..EDGES_PER_NODE {
            let v = adj[u * EDGES_PER_NODE + k];
            let nd = d + w[u * EDGES_PER_NODE + k];
            if nd < dist[v] {
                dist[v] = nd;
                heap.push(Reverse((nd, v)));
            }
        }
    }

    assert_eq!(dist[0], 0, "self-check failed: dist[0] should be 0");
    let mut ring_bound: i64 = 0;
    let mut total: i64 = 0;
    for i in 0..n {
        if i > 0 {
            ring_bound += w[(i - 1) * EDGES_PER_NODE];
        }
        assert!(
            dist[i] >= 0 && dist[i] <= ring_bound,
            "self-check failed: dist[{}] out of bounds",
            i
        );
        total += dist[i];
    }

    println!("{}", total);
}
