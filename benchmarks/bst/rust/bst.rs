use std::env;

struct Node {
    val: i64,
    left: Option<Box<Node>>,
    right: Option<Box<Node>>,
}

impl Node {
    fn new(val: i64) -> Self {
        Node { val, left: None, right: None }
    }

    fn insert(&mut self, val: i64) {
        if val < self.val {
            match self.left {
                Some(ref mut l) => l.insert(val),
                None => self.left = Some(Box::new(Node::new(val))),
            }
        } else {
            match self.right {
                Some(ref mut r) => r.insert(val),
                None => self.right = Some(Box::new(Node::new(val))),
            }
        }
    }

    fn inorder(&self, prev: &mut i64, first: &mut bool, ok: &mut bool, max_val: &mut i64, count: &mut i64) {
        if let Some(ref l) = self.left {
            l.inorder(prev, first, ok, max_val, count);
        }
        if !*first && self.val < *prev {
            *ok = false;
        }
        *first = false;
        *prev = self.val;
        *max_val = self.val;
        *count += 1;
        if let Some(ref r) = self.right {
            r.inorder(prev, first, ok, max_val, count);
        }
    }
}

fn main() {
    let n: i64 = env::args().nth(1).map(|s| s.parse().unwrap()).unwrap_or(300_000);

    let mut state: u64 = 42;
    let mut next_rand = || -> i64 {
        state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
        (state >> 33) as i64
    };

    let mut root = Node::new(next_rand());
    for _ in 1..n {
        let v = next_rand();
        root.insert(v);
    }

    let mut prev = 0i64;
    let mut first = true;
    let mut ok = true;
    let mut max_val = 0i64;
    let mut count = 0i64;
    root.inorder(&mut prev, &mut first, &mut ok, &mut max_val, &mut count);

    assert!(ok && count == n, "self-check failed: in-order traversal not sorted or count mismatch");
    println!("{}", max_val);
}
