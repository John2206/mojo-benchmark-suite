use std::env;

const MAX_ITER: u32 = 1000;

fn escape_iters(cr: f64, ci: f64) -> u32 {
    let mut zr = 0.0f64;
    let mut zi = 0.0f64;
    let mut i = 0;
    while i < MAX_ITER {
        let zr2 = zr * zr;
        let zi2 = zi * zi;
        if zr2 + zi2 > 4.0 {
            break;
        }
        let new_zi = 2.0 * zr * zi + ci;
        zr = zr2 - zi2 + cr;
        zi = new_zi;
        i += 1;
    }
    i
}

fn main() {
    let n: i64 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(800);

    assert_eq!(escape_iters(0.0, 0.0), MAX_ITER, "self-check failed: origin should never escape");
    assert!(escape_iters(2.0, 2.0) < MAX_ITER, "self-check failed: far point should escape quickly");

    let mut count: i64 = 0;
    for py in 0..n {
        let ci = -1.5 + 3.0 * (py as f64) / (n as f64);
        for px in 0..n {
            let cr = -2.0 + 3.0 * (px as f64) / (n as f64);
            if escape_iters(cr, ci) == MAX_ITER {
                count += 1;
            }
        }
    }
    println!("{}", count);
}
