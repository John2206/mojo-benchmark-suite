use std::collections::HashMap;
use std::env;

const CAPACITY: usize = 1000;
const WORKING_SET: i64 = 800;

struct Cache {
    map: HashMap<i64, usize>,
    key_arr: Vec<i64>,
    prev_arr: Vec<i32>,
    next_arr: Vec<i32>,
    head: i32,
    tail: i32,
    size: usize,
    hit_count: i64,
}

impl Cache {
    fn new() -> Self {
        Cache {
            map: HashMap::new(),
            key_arr: vec![0; CAPACITY],
            prev_arr: vec![-1; CAPACITY],
            next_arr: vec![-1; CAPACITY],
            head: -1,
            tail: -1,
            size: 0,
            hit_count: 0,
        }
    }

    fn list_remove(&mut self, slot: usize) {
        let p = self.prev_arr[slot];
        let nx = self.next_arr[slot];
        if p != -1 {
            self.next_arr[p as usize] = nx;
        } else {
            self.head = nx;
        }
        if nx != -1 {
            self.prev_arr[nx as usize] = p;
        } else {
            self.tail = p;
        }
    }

    fn list_push_front(&mut self, slot: usize) {
        self.prev_arr[slot] = -1;
        self.next_arr[slot] = self.head;
        if self.head != -1 {
            self.prev_arr[self.head as usize] = slot as i32;
        }
        self.head = slot as i32;
        if self.tail == -1 {
            self.tail = slot as i32;
        }
    }

    fn access_key(&mut self, key: i64) {
        if let Some(&slot) = self.map.get(&key) {
            self.hit_count += 1;
            self.list_remove(slot);
            self.list_push_front(slot);
            return;
        }

        let slot: usize;
        if self.size < CAPACITY {
            slot = self.size;
            self.size += 1;
        } else {
            slot = self.tail as usize;
            self.list_remove(slot);
            self.map.remove(&self.key_arr[slot]);
        }
        self.key_arr[slot] = key;
        self.map.insert(key, slot);
        self.list_push_front(slot);
    }
}

fn main() {
    let n: i64 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(2_000_000);

    let mut cache = Cache::new();
    for i in 0..(CAPACITY as i64 + 50) {
        cache.access_key(i);
    }
    assert!(!cache.map.contains_key(&0), "self-check failed: key 0 should have been evicted");
    assert!(
        cache.map.contains_key(&(CAPACITY as i64 + 49)),
        "self-check failed: most recently used key should still be cached"
    );
    assert_eq!(cache.size, CAPACITY, "self-check failed: cache size should equal capacity after overfill");

    let mut cache = Cache::new();
    for i in 0..n {
        cache.access_key(i % WORKING_SET);
    }

    let expected = if n > WORKING_SET { n - WORKING_SET } else { 0 };
    assert_eq!(cache.hit_count, expected, "self-check failed: hit count mismatch");

    println!("{}", cache.hit_count);
}
