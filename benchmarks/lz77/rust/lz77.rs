use std::env;

const WINDOW: i64 = 4096;
const MAX_MATCH: usize = 255;
const MIN_MATCH: usize = 3;
const HASH_SIZE: usize = 8192;

struct Token {
    is_match: bool,
    offset: i64,
    length: usize,
    literal: u8,
}

fn hash3(data: &[u8], i: usize) -> usize {
    (((data[i] as usize) * 131 + data[i + 1] as usize) * 131 + data[i + 2] as usize) & (HASH_SIZE - 1)
}

fn lz77_encode(data: &[u8]) -> Vec<Token> {
    let n = data.len();
    let mut hash_table = vec![-1i64; HASH_SIZE];
    let mut tokens = Vec::new();
    let mut i: usize = 0;
    while i < n {
        let mut best_len = 0usize;
        let mut best_cand: i64 = -1;
        if i + 3 <= n {
            let h = hash3(data, i);
            let cand = hash_table[h];
            if cand != -1 && (i as i64 - cand) <= WINDOW {
                let cand_u = cand as usize;
                let mut match_len = 0usize;
                while match_len < MAX_MATCH && i + match_len < n && data[cand_u + match_len] == data[i + match_len] {
                    match_len += 1;
                }
                if match_len >= MIN_MATCH {
                    best_len = match_len;
                    best_cand = cand;
                }
            }
            hash_table[h] = i as i64;
        }
        if best_len >= MIN_MATCH {
            tokens.push(Token { is_match: true, offset: i as i64 - best_cand, length: best_len, literal: 0 });
            i += best_len;
        } else {
            tokens.push(Token { is_match: false, offset: 0, length: 0, literal: data[i] });
            i += 1;
        }
    }
    tokens
}

fn lz77_decode(tokens: &[Token]) -> Vec<u8> {
    let mut out: Vec<u8> = Vec::new();
    for t in tokens {
        if t.is_match {
            let start = out.len() as i64 - t.offset;
            for k in 0..t.length {
                let b = out[(start + k as i64) as usize];
                out.push(b);
            }
        } else {
            out.push(t.literal);
        }
    }
    out
}

fn main() {
    let n: usize = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(5_000_000);

    let mut pattern = [0u8; 64];
    for i in 0..64 {
        pattern[i] = ((i * 7 + 3) % 251) as u8;
    }
    let mut data = vec![0u8; n];
    for i in 0..n {
        let mut v = pattern[i % 64];
        if i % 97 == 0 {
            v = v.wrapping_add(1);
        }
        data[i] = v;
    }

    let tokens = lz77_encode(&data);
    let decoded = lz77_decode(&tokens);

    assert_eq!(decoded.len(), n, "self-check failed: roundtrip length mismatch");
    assert_eq!(decoded, data, "self-check failed: roundtrip byte mismatch");

    let compressed_bytes: i64 = tokens.iter().map(|t| if t.is_match { 4 } else { 2 }).sum();
    println!("{}", compressed_bytes);
}
