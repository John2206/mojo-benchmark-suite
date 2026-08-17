use std::env;

fn edit_distance(s1: &[u8], s2: &[u8]) -> i32 {
    let len1 = s1.len();
    let len2 = s2.len();
    let mut prev: Vec<i32> = (0..=len2 as i32).collect();
    let mut cur: Vec<i32> = vec![0; len2 + 1];

    for i in 1..=len1 {
        cur[0] = i as i32;
        for j in 1..=len2 {
            let cost = if s1[i - 1] == s2[j - 1] { 0 } else { 1 };
            let del = prev[j] + 1;
            let ins = cur[j - 1] + 1;
            let sub = prev[j - 1] + cost;
            cur[j] = del.min(ins).min(sub);
        }
        std::mem::swap(&mut prev, &mut cur);
    }

    prev[len2]
}

fn main() {
    let n: usize = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(5000);

    assert_eq!(
        edit_distance(b"kitten", b"sitting"),
        3,
        "self-check failed: edit_distance(kitten,sitting) mismatch"
    );

    const ALPHABET: &[u8; 4] = b"ACGT";
    let mut s1 = vec![0u8; n];
    let mut s2 = vec![0u8; n];
    for i in 0..n {
        let base = (i * 7 + 3) % 4;
        s1[i] = ALPHABET[base];
        s2[i] = if i % 5 == 4 { ALPHABET[(base + 1) % 4] } else { ALPHABET[base] };
    }

    println!("{}", edit_distance(&s1, &s2));
}
