use std::env;

const EDGES_PER_NODE: usize = 4;

fn main() {
    let n: usize = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(500_000);

    let mut adj = vec![0usize; n * EDGES_PER_NODE];
    let mut state: u64 = 42;
    let mut next_rand = |bound: usize| -> usize {
        state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
        ((state >> 33) as usize) % bound
    };
    for i in 0..n {
        adj[i * EDGES_PER_NODE] = (i + 1) % n;
        for k in 1..EDGES_PER_NODE {
            adj[i * EDGES_PER_NODE + k] = next_rand(n);
        }
    }

    let mut visited = vec![false; n];
    let mut queue = vec![0usize; n];
    let mut head = 0;
    let mut tail = 0;
    visited[0] = true;
    queue[tail] = 0;
    tail += 1;
    let mut visited_count: usize = 1;

    while head < tail {
        let node = queue[head];
        head += 1;
        for k in 0..EDGES_PER_NODE {
            let nxt = adj[node * EDGES_PER_NODE + k];
            if !visited[nxt] {
                visited[nxt] = true;
                visited_count += 1;
                queue[tail] = nxt;
                tail += 1;
            }
        }
    }

    assert_eq!(visited_count, n, "self-check failed: not all nodes reachable");
    println!("{}", visited_count);
}
