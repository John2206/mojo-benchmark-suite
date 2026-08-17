use std::env;

const ENC_TABLE: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

fn base64_encode(data: &[u8]) -> String {
    let mut out = Vec::with_capacity(((data.len() + 2) / 3) * 4);
    let mut i = 0;
    while i + 3 <= data.len() {
        let (b0, b1, b2) = (data[i], data[i + 1], data[i + 2]);
        out.push(ENC_TABLE[(b0 >> 2) as usize]);
        out.push(ENC_TABLE[(((b0 & 0x03) << 4) | (b1 >> 4)) as usize]);
        out.push(ENC_TABLE[(((b1 & 0x0F) << 2) | (b2 >> 6)) as usize]);
        out.push(ENC_TABLE[(b2 & 0x3F) as usize]);
        i += 3;
    }
    let rem = data.len() - i;
    if rem == 1 {
        let b0 = data[i];
        out.push(ENC_TABLE[(b0 >> 2) as usize]);
        out.push(ENC_TABLE[((b0 & 0x03) << 4) as usize]);
        out.push(b'=');
        out.push(b'=');
    } else if rem == 2 {
        let (b0, b1) = (data[i], data[i + 1]);
        out.push(ENC_TABLE[(b0 >> 2) as usize]);
        out.push(ENC_TABLE[(((b0 & 0x03) << 4) | (b1 >> 4)) as usize]);
        out.push(ENC_TABLE[((b1 & 0x0F) << 2) as usize]);
        out.push(b'=');
    }
    String::from_utf8(out).unwrap()
}

fn dec_value(c: u8) -> i32 {
    match c {
        b'A'..=b'Z' => (c - b'A') as i32,
        b'a'..=b'z' => (c - b'a') as i32 + 26,
        b'0'..=b'9' => (c - b'0') as i32 + 52,
        b'+' => 62,
        b'/' => 63,
        _ => -1,
    }
}

fn base64_decode(enc: &[u8]) -> Vec<u8> {
    let mut out = Vec::with_capacity((enc.len() / 4) * 3);
    let mut i = 0;
    while i < enc.len() {
        let v0 = dec_value(enc[i]);
        let v1 = dec_value(enc[i + 1]);
        let v2 = if enc[i + 2] == b'=' { -2 } else { dec_value(enc[i + 2]) };
        let v3 = if enc[i + 3] == b'=' { -2 } else { dec_value(enc[i + 3]) };
        out.push(((v0 << 2) | (v1 >> 4)) as u8);
        if v2 != -2 {
            out.push((((v1 & 0x0F) << 4) | (v2 >> 2)) as u8);
            if v3 != -2 {
                out.push((((v2 & 0x03) << 6) | v3) as u8);
            }
        }
        i += 4;
    }
    out
}

fn main() {
    let n: usize = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(20_000_000);

    assert_eq!(base64_encode(b""), "", "self-check failed: base64(\"\") mismatch");
    assert_eq!(base64_encode(b"f"), "Zg==", "self-check failed: base64(\"f\") mismatch");
    assert_eq!(base64_encode(b"fo"), "Zm8=", "self-check failed: base64(\"fo\") mismatch");
    assert_eq!(base64_encode(b"foo"), "Zm9v", "self-check failed: base64(\"foo\") mismatch");

    let mut buf = vec![0u8; n];
    for i in 0..n {
        buf[i] = ((i * 131 + 7) % 256) as u8;
    }

    let encoded = base64_encode(&buf);
    let decoded = base64_decode(encoded.as_bytes());
    assert_eq!(decoded, buf, "self-check failed: roundtrip mismatch");

    let sum: u64 = encoded.bytes().map(|b| b as u64).sum();
    println!("{}", sum);
}
