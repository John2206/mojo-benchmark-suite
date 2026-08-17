#include <stdio.h>
#include <stdlib.h>

#define CAPACITY 1000
#define WORKING_SET 800
#define TABLE_CAP 4096
#define EMPTY (-1L)
#define TOMBSTONE (-2L)

typedef struct {
    long key;
    int value;
} Entry;

static Entry table[TABLE_CAP];
static int tombstones;
static long key_arr[CAPACITY];
static int prev_arr[CAPACITY];
static int next_arr[CAPACITY];
static int head, tail, size;
static long hit_count;

static unsigned long hash_long(long key) {
    unsigned long h = (unsigned long)key;
    h ^= h >> 33;
    h *= 0xff51afd7ed558ccdUL;
    h ^= h >> 33;
    return h;
}

static void hm_init(void) {
    for (int i = 0; i < TABLE_CAP; i++) table[i].key = EMPTY;
    tombstones = 0;
}

static int hm_get(long key) {
    unsigned long i = hash_long(key) & (TABLE_CAP - 1);
    while (table[i].key != EMPTY) {
        if (table[i].key == key) return table[i].value;
        i = (i + 1) & (TABLE_CAP - 1);
    }
    return -1;
}

static void hm_put(long key, int value) {
    unsigned long i = hash_long(key) & (TABLE_CAP - 1);
    long first_free = -1;
    while (table[i].key != EMPTY) {
        if (table[i].key == key) {
            table[i].value = value;
            return;
        }
        if (first_free == -1 && table[i].key == TOMBSTONE) first_free = (long)i;
        i = (i + 1) & (TABLE_CAP - 1);
    }
    long slot = (first_free != -1) ? first_free : (long)i;
    table[slot].key = key;
    table[slot].value = value;
}

static void hm_delete(long key) {
    unsigned long i = hash_long(key) & (TABLE_CAP - 1);
    while (table[i].key != EMPTY) {
        if (table[i].key == key) {
            table[i].key = TOMBSTONE;
            tombstones++;
            return;
        }
        i = (i + 1) & (TABLE_CAP - 1);
    }
}

static void hm_rebuild(void) {
    hm_init();
    for (int slot = 0; slot < size; slot++) {
        hm_put(key_arr[slot], slot);
    }
}

static void list_remove(int slot) {
    int p = prev_arr[slot];
    int nx = next_arr[slot];
    if (p != -1) next_arr[p] = nx; else head = nx;
    if (nx != -1) prev_arr[nx] = p; else tail = p;
}

static void list_push_front(int slot) {
    prev_arr[slot] = -1;
    next_arr[slot] = head;
    if (head != -1) prev_arr[head] = slot;
    head = slot;
    if (tail == -1) tail = slot;
}

static void cache_reset(void) {
    hm_init();
    head = -1;
    tail = -1;
    size = 0;
    hit_count = 0;
}

static void access_key(long key) {
    int slot = hm_get(key);
    if (slot != -1) {
        hit_count++;
        list_remove(slot);
        list_push_front(slot);
        return;
    }

    if (size < CAPACITY) {
        slot = size;
        size++;
    } else {
        slot = tail;
        list_remove(slot);
        hm_delete(key_arr[slot]);
    }
    key_arr[slot] = key;
    if (tombstones > CAPACITY) {
        hm_rebuild();
    }
    hm_put(key, slot);
    list_push_front(slot);
}

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 2000000;

    /* Self-check: overfill by 50 keys past capacity, sequentially, and
     * confirm the oldest key was evicted while the newest is retained --
     * exercises the eviction/delete/rebuild path with a fixed,
     * size-independent check. */
    cache_reset();
    for (long i = 0; i < CAPACITY + 50; i++) {
        access_key(i);
    }
    if (hm_get(0) != -1) {
        fprintf(stderr, "self-check failed: key 0 should have been evicted\n");
        return 1;
    }
    if (hm_get(CAPACITY + 49) == -1) {
        fprintf(stderr, "self-check failed: most recently used key should still be cached\n");
        return 1;
    }
    if (size != CAPACITY) {
        fprintf(stderr, "self-check failed: cache size should equal capacity after overfill\n");
        return 1;
    }

    /* Main workload: a working set smaller than capacity, so after the
     * first WORKING_SET accesses (all misses), every later access is a
     * guaranteed hit -- exact hit count for any n is max(0, n - WORKING_SET). */
    cache_reset();
    for (long i = 0; i < n; i++) {
        access_key(i % WORKING_SET);
    }

    long expected = n > WORKING_SET ? n - WORKING_SET : 0;
    if (hit_count != expected) {
        fprintf(stderr, "self-check failed: hit count mismatch: got %ld, expected %ld\n", hit_count, expected);
        return 1;
    }

    printf("%ld\n", hit_count);
    return 0;
}
