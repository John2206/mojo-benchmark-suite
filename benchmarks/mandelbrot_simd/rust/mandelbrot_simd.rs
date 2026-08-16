use std::arch::x86_64::*;
use std::env;

const MAX_ITER: i64 = 1000;
const W: usize = 4;

#[target_feature(enable = "avx2")]
unsafe fn escape_counts_row(cr: [f64; W], ci: f64) -> [i64; W] {
    let mut zr = _mm256_setzero_pd();
    let mut zi = _mm256_setzero_pd();
    let cr_vec = _mm256_loadu_pd(cr.as_ptr());
    let ci_vec = _mm256_set1_pd(ci);
    let four = _mm256_set1_pd(4.0);
    let mut iters = _mm256_setzero_si256();
    let mut active = _mm256_set1_epi64x(-1);

    for _ in 0..MAX_ITER {
        let zr2 = _mm256_mul_pd(zr, zr);
        let zi2 = _mm256_mul_pd(zi, zi);
        let mag2 = _mm256_add_pd(zr2, zi2);
        let cmp = _mm256_castpd_si256(_mm256_cmp_pd(mag2, four, _CMP_LE_OQ));
        let still = _mm256_and_si256(cmp, active);

        if _mm256_testz_si256(still, still) != 0 {
            break;
        }

        let new_zi = _mm256_add_pd(_mm256_mul_pd(_mm256_set1_pd(2.0), _mm256_mul_pd(zr, zi)), ci_vec);
        let new_zr = _mm256_add_pd(_mm256_sub_pd(zr2, zi2), cr_vec);
        let still_d = _mm256_castsi256_pd(still);
        zr = _mm256_blendv_pd(zr, new_zr, still_d);
        zi = _mm256_blendv_pd(zi, new_zi, still_d);

        let iters_plus1 = _mm256_add_epi64(iters, _mm256_set1_epi64x(1));
        iters = _mm256_blendv_epi8(iters, iters_plus1, still);
        active = still;
    }

    let mut out = [0i64; W];
    _mm256_storeu_si256(out.as_mut_ptr() as *mut __m256i, iters);
    out
}

fn main() {
    if !is_x86_feature_detected!("avx2") {
        eprintln!("AVX2 not supported on this CPU");
        std::process::exit(1);
    }

    let n: i64 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(800);

    unsafe {
        let origin = escape_counts_row([0.0; W], 0.0);
        assert!(
            origin.iter().all(|&x| x == MAX_ITER),
            "self-check failed: origin should never escape"
        );

        let far = escape_counts_row([2.0; W], 2.0);
        assert!(
            far.iter().all(|&x| x < MAX_ITER),
            "self-check failed: far point should escape quickly"
        );

        let groups = n / W as i64;
        let mut count: i64 = 0;
        for py in 0..n {
            let ci = -1.5 + 3.0 * (py as f64) / (n as f64);
            for gx in 0..groups {
                let mut cr = [0.0; W];
                for lane in 0..W {
                    let px = gx * W as i64 + lane as i64;
                    cr[lane] = -2.0 + 3.0 * (px as f64) / (n as f64);
                }
                let iters = escape_counts_row(cr, ci);
                for &it in iters.iter() {
                    if it == MAX_ITER {
                        count += 1;
                    }
                }
            }
        }

        println!("{}", count);
    }
}
