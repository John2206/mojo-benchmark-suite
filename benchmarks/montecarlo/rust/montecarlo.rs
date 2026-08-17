use std::env;

const PI: f64 = 3.14159265358979323846;

struct Lcg {
    state: u32,
}

impl Lcg {
    fn next(&mut self) -> f64 {
        self.state = self.state.wrapping_mul(1103515245).wrapping_add(12345) & 0x7fffffff;
        self.state as f64 / 2147483648.0
    }
}

fn main() {
    let n: i64 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(50_000_000);

    let mut lcg = Lcg { state: 1 };
    let mut inside: i64 = 0;
    for _ in 0..n {
        let x = lcg.next();
        let y = lcg.next();
        if x * x + y * y <= 1.0 {
            inside += 1;
        }
    }

    let pi_estimate = 4.0 * inside as f64 / n as f64;
    let tolerance = 10.0 / (n as f64).sqrt();

    assert!(
        (pi_estimate - PI).abs() < tolerance,
        "self-check failed: pi estimate out of tolerance: {}",
        pi_estimate
    );

    println!("{:.6}", pi_estimate);
}
