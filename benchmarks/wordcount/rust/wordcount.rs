use std::collections::HashMap;
use std::env;

const VOCAB: [&str; 20] = [
    "the", "of", "and", "a", "to", "in", "is", "you", "that", "it", "he", "was", "for", "on",
    "are", "as", "with", "his", "they", "at",
];

fn main() {
    let n: u64 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(2_000_000);

    let mut state: u64 = 42;
    let mut counts: HashMap<&str, u64> = HashMap::new();
    for _ in 0..n {
        state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
        let idx = ((state >> 33) as usize) % VOCAB.len();
        *counts.entry(VOCAB[idx]).or_insert(0) += 1;
    }

    let total: u64 = counts.values().sum();
    assert_eq!(total, n, "self-check failed: counts do not sum to n");

    println!("{}", counts.len());
}
