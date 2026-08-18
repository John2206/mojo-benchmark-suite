use std::collections::HashMap;
use std::env;

const VOCAB: [&str; 20] = [
    "the", "of", "and", "a", "to", "in", "is", "you", "that", "it", "he", "was", "for", "on",
    "are", "as", "with", "his", "they", "at",
];

struct Lcg {
    state: u32,
}

impl Lcg {
    fn next(&mut self) -> u64 {
        self.state = self.state.wrapping_mul(1103515245).wrapping_add(12345) & 0x7fffffff;
        self.state as u64
    }
}

fn main() {
    let n: u64 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(2_000_000);

    let mut lcg = Lcg { state: 42 };
    let mut counts: HashMap<&str, u64> = HashMap::new();
    for _ in 0..n {
        let idx = (lcg.next() % VOCAB.len() as u64) as usize;
        *counts.entry(VOCAB[idx]).or_insert(0) += 1;
    }

    let total: u64 = counts.values().sum();
    assert_eq!(total, n, "self-check failed: counts do not sum to n");

    println!("{}", counts.len());
}
