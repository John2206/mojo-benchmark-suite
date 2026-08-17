import java.util.HashMap;
import java.util.Map;

public class Lru_cache {
    static final int CAPACITY = 1000;
    static final long WORKING_SET = 800;

    static Map<Long, Integer> map = new HashMap<>();
    static long[] keyArr = new long[CAPACITY];
    static int[] prevArr = new int[CAPACITY];
    static int[] nextArr = new int[CAPACITY];
    static int head, tail, size;
    static long hitCount;

    static void listRemove(int slot) {
        int p = prevArr[slot];
        int nx = nextArr[slot];
        if (p != -1) nextArr[p] = nx; else head = nx;
        if (nx != -1) prevArr[nx] = p; else tail = p;
    }

    static void listPushFront(int slot) {
        prevArr[slot] = -1;
        nextArr[slot] = head;
        if (head != -1) prevArr[head] = slot;
        head = slot;
        if (tail == -1) tail = slot;
    }

    static void reset() {
        map = new HashMap<>();
        head = -1;
        tail = -1;
        size = 0;
        hitCount = 0;
    }

    static void accessKey(long key) {
        Integer existing = map.get(key);
        if (existing != null) {
            hitCount++;
            listRemove(existing);
            listPushFront(existing);
            return;
        }

        int slot;
        if (size < CAPACITY) {
            slot = size;
            size++;
        } else {
            slot = tail;
            listRemove(slot);
            map.remove(keyArr[slot]);
        }
        keyArr[slot] = key;
        map.put(key, slot);
        listPushFront(slot);
    }

    public static void main(String[] args) {
        long n = args.length > 0 ? Long.parseLong(args[0]) : 2_000_000;

        reset();
        for (long i = 0; i < CAPACITY + 50; i++) {
            accessKey(i);
        }
        if (map.containsKey(0L)) {
            System.err.println("self-check failed: key 0 should have been evicted");
            System.exit(1);
        }
        if (!map.containsKey((long) (CAPACITY + 49))) {
            System.err.println("self-check failed: most recently used key should still be cached");
            System.exit(1);
        }
        if (size != CAPACITY) {
            System.err.println("self-check failed: cache size should equal capacity after overfill");
            System.exit(1);
        }

        reset();
        for (long i = 0; i < n; i++) {
            accessKey(i % WORKING_SET);
        }

        long expected = n > WORKING_SET ? n - WORKING_SET : 0;
        if (hitCount != expected) {
            System.err.println("self-check failed: hit count mismatch: got " + hitCount + ", expected " + expected);
            System.exit(1);
        }

        System.out.println(hitCount);
    }
}
