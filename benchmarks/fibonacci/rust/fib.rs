use std::env;

fn fib(n: u64) -> u64 {
    if n < 2 { n } else { fib(n - 1) + fib(n - 2) }
}

fn main() {
    let n: u64 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(32);
    assert_eq!(fib(10), 55, "self-check failed: fib(10) != 55");
    println!("{}", fib(n));
}
