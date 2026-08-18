use std::env;

struct Lcg {
    state: u32,
}

impl Lcg {
    fn next(&mut self) -> i64 {
        self.state = self.state.wrapping_mul(1103515245).wrapping_add(12345) & 0x7fffffff;
        self.state as i64
    }
}

fn main() {
    let n: usize = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(2_000_000);

    let mut lcg = Lcg { state: 42 };
    let mut arr: Vec<i64> = (0..n).map(|_| lcg.next()).collect();

    arr.sort();

    assert!(
        arr.windows(2).all(|w| w[0] <= w[1]),
        "self-check failed: array not sorted"
    );
    println!("{}", arr[n - 1]);
}
