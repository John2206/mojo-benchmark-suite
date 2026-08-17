use std::env;

fn build_table() -> [u32; 256] {
    let mut table = [0u32; 256];
    for i in 0..256u32 {
        let mut crc = i;
        for _ in 0..8 {
            if crc & 1 != 0 {
                crc = (crc >> 1) ^ 0xEDB88320;
            } else {
                crc >>= 1;
            }
        }
        table[i as usize] = crc;
    }
    table
}

fn crc32_compute(table: &[u32; 256], data: &[u8]) -> u32 {
    let mut crc: u32 = 0xFFFFFFFF;
    for &b in data {
        crc = table[((crc ^ b as u32) & 0xFF) as usize] ^ (crc >> 8);
    }
    crc ^ 0xFFFFFFFF
}

fn main() {
    let n: usize = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(50_000_000);

    let table = build_table();

    assert_eq!(crc32_compute(&table, b""), 0x00000000, "self-check failed: CRC32(\"\") mismatch");
    assert_eq!(crc32_compute(&table, b"123456789"), 0xCBF43926, "self-check failed: CRC32(\"123456789\") mismatch");

    let mut buf = vec![0u8; n];
    for i in 0..n {
        buf[i] = ((i * 131 + 7) % 256) as u8;
    }

    let result = crc32_compute(&table, &buf);
    println!("{:08x}", result);
}
