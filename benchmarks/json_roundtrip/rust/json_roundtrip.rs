use std::env;
use std::fmt::Write as _;

fn parse_int(bytes: &[u8], pos: &mut usize) -> i64 {
    let mut val: i64 = 0;
    while bytes[*pos].is_ascii_digit() {
        val = val * 10 + (bytes[*pos] - b'0') as i64;
        *pos += 1;
    }
    val
}

fn parse_decimal1(bytes: &[u8], pos: &mut usize) -> f64 {
    let whole = parse_int(bytes, pos);
    *pos += 1; // '.'
    let frac = (bytes[*pos] - b'0') as f64;
    *pos += 1;
    whole as f64 + frac / 10.0
}

fn main() {
    let n: i64 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(200_000);

    // --- encode ---
    let mut buf = String::with_capacity((n as usize) * 48 + 16);
    buf.push('[');
    for i in 0..n {
        if i > 0 {
            buf.push(',');
        }
        write!(buf, "{{\"id\":{},\"name\":\"item{}\",\"value\":{:.1}}}", i, i, i as f64 * 0.5).unwrap();
    }
    buf.push(']');

    // --- decode ---
    let bytes = buf.as_bytes();
    let mut pos = 1usize; // skip '['
    let mut id_sum: i64 = 0;
    let mut decoded_count: i64 = 0;
    while bytes[pos] != b']' {
        pos += 1; // '{'
        pos += "\"id\":".len();
        let id = parse_int(bytes, &mut pos);
        pos += ",\"name\":\"item".len();
        parse_int(bytes, &mut pos); // skip digits in name, not re-checked
        pos += "\",\"value\":".len();
        let value = parse_decimal1(bytes, &mut pos);
        pos += 1; // '}'
        if bytes[pos] == b',' {
            pos += 1;
        }

        assert_eq!(value, id as f64 * 0.5, "self-check failed: decoded value mismatch for id {}", id);
        id_sum += id;
        decoded_count += 1;
    }

    let expected_sum = n * (n - 1) / 2;
    assert!(id_sum == expected_sum && decoded_count == n, "self-check failed: id sum or count mismatch");

    println!("{}", id_sum);
}
