use std::env;

const STEPS: usize = 100;
const G: f64 = 1e-4;
const DT: f64 = 1e-3;

fn main() {
    let n: usize = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(300);

    let mut mass = vec![0.0f64; n];
    let mut px = vec![0.0f64; n];
    let mut py = vec![0.0f64; n];
    let mut pz = vec![0.0f64; n];
    let mut vx = vec![0.0f64; n];
    let mut vy = vec![0.0f64; n];
    let mut vz = vec![0.0f64; n];

    for i in 0..n {
        mass[i] = 1.0 + i as f64;
        px[i] = i as f64 * 0.1;
        py[i] = i as f64 * 0.2;
        pz[i] = i as f64 * 0.3;
    }

    for _ in 0..STEPS {
        for i in 0..n {
            for j in (i + 1)..n {
                let dx = px[j] - px[i];
                let dy = py[j] - py[i];
                let dz = pz[j] - pz[i];
                let dist2 = dx * dx + dy * dy + dz * dz + 1e-9;
                let inv_dist3 = 1.0 / (dist2 * dist2.sqrt());
                let fx = G * dx * inv_dist3;
                let fy = G * dy * inv_dist3;
                let fz = G * dz * inv_dist3;
                vx[i] += fx * mass[j] * DT;
                vy[i] += fy * mass[j] * DT;
                vz[i] += fz * mass[j] * DT;
                vx[j] -= fx * mass[i] * DT;
                vy[j] -= fy * mass[i] * DT;
                vz[j] -= fz * mass[i] * DT;
            }
        }
        for i in 0..n {
            px[i] += vx[i] * DT;
            py[i] += vy[i] * DT;
            pz[i] += vz[i] * DT;
        }
    }

    let momentum_x: f64 = (0..n).map(|i| mass[i] * vx[i]).sum();
    assert!(
        momentum_x.abs() < 1e-6,
        "self-check failed: momentum not conserved ({})",
        momentum_x
    );

    println!("{:.6} {:.6} {:.6}", px[0], py[0], pz[0]);
}
