use std::env;

fn main() {
    let n: usize = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(2_000_000);

    let mut state: u64 = 42;
    let mut arr: Vec<i64> = (0..n)
        .map(|_| {
            state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
            (state >> 33) as i64
        })
        .collect();

    arr.sort();

    assert!(
        arr.windows(2).all(|w| w[0] <= w[1]),
        "self-check failed: array not sorted"
    );
    println!("{}", arr[n - 1]);
}
