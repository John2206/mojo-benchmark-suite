use std::env;
use std::thread;

const NUM_THREADS: i64 = 4;

fn is_prime(x: i64) -> bool {
    if x < 2 {
        return false;
    }
    if x % 2 == 0 {
        return x == 2;
    }
    let mut d = 3;
    while d * d <= x {
        if x % d == 0 {
            return false;
        }
        d += 2;
    }
    true
}

fn main() {
    let n: i64 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(2_000_000);

    assert!(
        is_prime(2) && is_prime(97) && !is_prime(100) && !is_prime(1),
        "self-check failed: is_prime disagrees with known facts"
    );

    let chunk = n / NUM_THREADS;
    let mut handles = Vec::new();
    for i in 0..NUM_THREADS {
        let start = (i * chunk).max(2);
        let end = if i == NUM_THREADS - 1 { n } else { (i + 1) * chunk };
        handles.push(thread::spawn(move || {
            let mut count = 0i64;
            for x in start..end {
                if is_prime(x) {
                    count += 1;
                }
            }
            count
        }));
    }

    let total: i64 = handles.into_iter().map(|h| h.join().unwrap()).sum();
    println!("{}", total);
}
