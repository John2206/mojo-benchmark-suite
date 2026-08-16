use std::env;

fn main() {
    let n: usize = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(400);

    let mut a = vec![0.0f64; n * n];
    let mut b = vec![0.0f64; n * n];
    for i in 0..n {
        for j in 0..n {
            a[i * n + j] = ((i * 3 + j) % 13) as f64;
            b[i * n + j] = ((i + j * 2) % 17) as f64;
        }
    }

    let mut c = vec![0.0f64; n * n];
    for i in 0..n {
        for k in 0..n {
            let aik = a[i * n + k];
            for j in 0..n {
                c[i * n + j] += aik * b[k * n + j];
            }
        }
    }

    let expected: f64 = (0..n).map(|k| a[k] * b[k * n]).sum();
    assert_eq!(c[0], expected, "self-check failed: c[0][0] mismatch");

    println!("{:.2}", c[(n - 1) * n + (n - 1)]);
}
