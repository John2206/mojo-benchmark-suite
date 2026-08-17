use std::env;
use std::f64::consts::PI;

fn next_pow2(n: i64) -> i64 {
    let mut p: i64 = 1;
    while p < n {
        p <<= 1;
    }
    p
}

fn fft(re: &mut [f64], im: &mut [f64], invert: bool) {
    let n = re.len();
    let mut j = 0usize;
    for i in 1..n {
        let mut bit = n >> 1;
        while j & bit != 0 {
            j ^= bit;
            bit >>= 1;
        }
        j ^= bit;
        if i < j {
            re.swap(i, j);
            im.swap(i, j);
        }
    }

    let mut length = 2usize;
    while length <= n {
        let ang = 2.0 * PI / (length as f64) * (if invert { 1.0 } else { -1.0 });
        let wlen_re = ang.cos();
        let wlen_im = ang.sin();
        let mut i = 0;
        while i < n {
            let mut w_re = 1.0;
            let mut w_im = 0.0;
            for k in i..(i + length / 2) {
                let u_re = re[k];
                let u_im = im[k];
                let v_re = re[k + length / 2] * w_re - im[k + length / 2] * w_im;
                let v_im = re[k + length / 2] * w_im + im[k + length / 2] * w_re;
                re[k] = u_re + v_re;
                im[k] = u_im + v_im;
                re[k + length / 2] = u_re - v_re;
                im[k + length / 2] = u_im - v_im;
                let nw_re = w_re * wlen_re - w_im * wlen_im;
                let nw_im = w_re * wlen_im + w_im * wlen_re;
                w_re = nw_re;
                w_im = nw_im;
            }
            i += length;
        }
        length <<= 1;
    }

    if invert {
        for i in 0..n {
            re[i] /= n as f64;
            im[i] /= n as f64;
        }
    }
}

fn main() {
    let requested: i64 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(1_048_576);
    let n = next_pow2(requested) as usize;

    let mut re = vec![0.0f64; n];
    let mut im = vec![0.0f64; n];
    let mut orig = vec![0.0f64; n];
    for i in 0..n {
        let v = (i % 7) as f64 - 3.0;
        re[i] = v;
        orig[i] = v;
    }

    fft(&mut re, &mut im, false);
    fft(&mut re, &mut im, true);

    let mut max_err = 0.0f64;
    for i in 0..n {
        let err = (re[i] - orig[i]).abs().max(im[i].abs());
        if err > max_err {
            max_err = err;
        }
    }

    assert!(max_err < 1e-6, "self-check failed: roundtrip reconstruction error too large: {}", max_err);

    println!("{:e}", max_err);
}
