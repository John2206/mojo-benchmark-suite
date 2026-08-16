use std::env;

fn main() {
    let n: i64 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(5_000_000);

    let mut total: i64 = 0;
    for _ in 0..n {
        let arr: Vec<i64> = (0..64).collect();
        let sum: i64 = arr.iter().sum();
        total += sum;
    }

    assert_eq!(total, n * 2016, "self-check failed: total mismatch");
    println!("{}", total);
}
