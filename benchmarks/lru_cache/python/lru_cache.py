import sys

CAPACITY = 1000
WORKING_SET = 800


class Cache:
    def __init__(self):
        self.map = {}
        self.key_arr = [0] * CAPACITY
        self.prev_arr = [-1] * CAPACITY
        self.next_arr = [-1] * CAPACITY
        self.head = -1
        self.tail = -1
        self.size = 0
        self.hit_count = 0

    def list_remove(self, slot):
        p = self.prev_arr[slot]
        nx = self.next_arr[slot]
        if p != -1:
            self.next_arr[p] = nx
        else:
            self.head = nx
        if nx != -1:
            self.prev_arr[nx] = p
        else:
            self.tail = p

    def list_push_front(self, slot):
        self.prev_arr[slot] = -1
        self.next_arr[slot] = self.head
        if self.head != -1:
            self.prev_arr[self.head] = slot
        self.head = slot
        if self.tail == -1:
            self.tail = slot

    def access_key(self, key):
        slot = self.map.get(key, -1)
        if slot != -1:
            self.hit_count += 1
            self.list_remove(slot)
            self.list_push_front(slot)
            return

        if self.size < CAPACITY:
            slot = self.size
            self.size += 1
        else:
            slot = self.tail
            self.list_remove(slot)
            del self.map[self.key_arr[slot]]

        self.key_arr[slot] = key
        self.map[key] = slot
        self.list_push_front(slot)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000

    cache = Cache()
    for i in range(CAPACITY + 50):
        cache.access_key(i)
    assert 0 not in cache.map, "self-check failed: key 0 should have been evicted"
    assert (CAPACITY + 49) in cache.map, "self-check failed: most recently used key should still be cached"
    assert cache.size == CAPACITY, "self-check failed: cache size should equal capacity after overfill"

    cache = Cache()
    for i in range(n):
        cache.access_key(i % WORKING_SET)

    expected = n - WORKING_SET if n > WORKING_SET else 0
    assert cache.hit_count == expected, "self-check failed: hit count mismatch"

    print(cache.hit_count)


if __name__ == "__main__":
    main()
