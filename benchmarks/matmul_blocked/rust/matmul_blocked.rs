use std::env;

const BLOCK: usize = 32;

fn main() {
    let n: usize = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(600);

    let mut a = vec![0.0f64; n * n];
    let mut b = vec![0.0f64; n * n];
    for i in 0..n {
        for j in 0..n {
            a[i * n + j] = ((i * 3 + j) % 13) as f64;
            b[i * n + j] = ((i + j * 2) % 17) as f64;
        }
    }

    let mut c = vec![0.0f64; n * n];
    let mut ii = 0;
    while ii < n {
        let i_max = (ii + BLOCK).min(n);
        let mut kk = 0;
        while kk < n {
            let k_max = (kk + BLOCK).min(n);
            let mut jj = 0;
            while jj < n {
                let j_max = (jj + BLOCK).min(n);
                for i in ii..i_max {
                    for k in kk..k_max {
                        let aik = a[i * n + k];
                        for j in jj..j_max {
                            c[i * n + j] += aik * b[k * n + j];
                        }
                    }
                }
                jj += BLOCK;
            }
            kk += BLOCK;
        }
        ii += BLOCK;
    }

    let expected: f64 = (0..n).map(|k| a[k] * b[k * n]).sum();
    assert_eq!(c[0], expected, "self-check failed: c[0][0] mismatch");

    println!("{:.2}", c[(n - 1) * n + (n - 1)]);
}
