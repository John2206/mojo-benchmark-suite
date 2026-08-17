from std.sys import argv

comptime CAPACITY = 1000
comptime WORKING_SET = 800


struct Cache(Movable):
    var map: Dict[Int, Int]
    var key_arr: List[Int]
    var prev_arr: List[Int]
    var next_arr: List[Int]
    var head: Int
    var tail: Int
    var size: Int
    var hit_count: Int

    def __init__(out self):
        self.map = Dict[Int, Int]()
        self.key_arr = List[Int](length=CAPACITY, fill=0)
        self.prev_arr = List[Int](length=CAPACITY, fill=-1)
        self.next_arr = List[Int](length=CAPACITY, fill=-1)
        self.head = -1
        self.tail = -1
        self.size = 0
        self.hit_count = 0

    def list_remove(mut self, slot: Int):
        var p = self.prev_arr[slot]
        var nx = self.next_arr[slot]
        if p != -1:
            self.next_arr[p] = nx
        else:
            self.head = nx
        if nx != -1:
            self.prev_arr[nx] = p
        else:
            self.tail = p

    def list_push_front(mut self, slot: Int):
        self.prev_arr[slot] = -1
        self.next_arr[slot] = self.head
        if self.head != -1:
            self.prev_arr[self.head] = slot
        self.head = slot
        if self.tail == -1:
            self.tail = slot

    def access_key(mut self, key: Int):
        var existing = self.map.get(key, -1)
        if existing != -1:
            self.hit_count += 1
            self.list_remove(existing)
            self.list_push_front(existing)
            return

        var slot: Int
        if self.size < CAPACITY:
            slot = self.size
            self.size += 1
        else:
            slot = self.tail
            self.list_remove(slot)
            _ = self.map.pop(self.key_arr[slot], -1)
        self.key_arr[slot] = key
        self.map[key] = slot
        self.list_push_front(slot)


def main() raises:
    var args = argv()
    var n = 2_000_000
    if len(args) > 1:
        n = atol(args[1])

    var cache = Cache()
    for i in range(CAPACITY + 50):
        cache.access_key(i)
    if cache.map.get(0, -1) != -1:
        raise Error("self-check failed: key 0 should have been evicted")
    if cache.map.get(CAPACITY + 49, -1) == -1:
        raise Error("self-check failed: most recently used key should still be cached")
    if cache.size != CAPACITY:
        raise Error("self-check failed: cache size should equal capacity after overfill")

    cache = Cache()
    for i in range(n):
        cache.access_key(i % WORKING_SET)

    var expected = 0
    if n > WORKING_SET:
        expected = n - WORKING_SET
    if cache.hit_count != expected:
        raise Error("self-check failed: hit count mismatch")

    print(cache.hit_count)
