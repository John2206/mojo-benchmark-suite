use std::env;

fn parse_group(s: &str) -> Option<u32> {
    if s.is_empty() || s.len() > 3 || !s.bytes().all(|b| b.is_ascii_digit()) {
        return None;
    }
    let val: u32 = s.parse().ok()?;
    if val > 255 {
        None
    } else {
        Some(val)
    }
}

fn is_valid_ip(s: &str) -> bool {
    let parts: Vec<&str> = s.split('.').collect();
    parts.len() == 4 && parts.iter().all(|p| parse_group(p).is_some())
}

fn main() {
    let n: u64 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(2_000_000);

    assert!(is_valid_ip("192.168.1.1"), "self-check failed: known-valid IP rejected");
    assert!(!is_valid_ip("999.1.1.1"), "self-check failed: known-invalid IP accepted");
    assert!(!is_valid_ip("1.2.3"), "self-check failed: known-invalid IP accepted");

    let mut state: u64 = 42;
    let mut next = || {
        state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
        (state >> 33) as u32
    };

    let mut valid: u64 = 0;
    for _ in 0..n {
        let max_val = if next() % 10 < 7 { 255 } else { 999 };
        let a = next() % (max_val + 1);
        let b = next() % (max_val + 1);
        let c = next() % (max_val + 1);
        let d = next() % (max_val + 1);
        let s = format!("{}.{}.{}.{}", a, b, c, d);
        if is_valid_ip(&s) {
            valid += 1;
        }
    }

    println!("{}", valid);
}
