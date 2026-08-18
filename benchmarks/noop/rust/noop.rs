use std::env;

fn main() {
    let _n: i64 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(0);
    println!("0");
}
