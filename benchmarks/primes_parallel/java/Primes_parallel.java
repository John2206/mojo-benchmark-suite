public class Primes_parallel {
    static final int NUM_THREADS = 4;

    static boolean isPrime(long x) {
        if (x < 2) return false;
        if (x % 2 == 0) return x == 2;
        for (long d = 3; d * d <= x; d += 2) {
            if (x % d == 0) return false;
        }
        return true;
    }

    public static void main(String[] args) throws InterruptedException {
        long n = args.length > 0 ? Long.parseLong(args[0]) : 2_000_000;

        if (!isPrime(2) || !isPrime(97) || isPrime(100) || isPrime(1)) {
            System.err.println("self-check failed: is_prime disagrees with known facts");
            System.exit(1);
        }

        long chunk = n / NUM_THREADS;
        Thread[] threads = new Thread[NUM_THREADS];
        long[] counts = new long[NUM_THREADS];
        for (int i = 0; i < NUM_THREADS; i++) {
            final int idx = i;
            final long start = Math.max(idx * chunk, 2);
            final long end = (idx == NUM_THREADS - 1) ? n : (idx + 1) * chunk;
            threads[idx] = new Thread(() -> {
                long count = 0;
                for (long x = start; x < end; x++) {
                    if (isPrime(x)) count++;
                }
                counts[idx] = count;
            });
            threads[idx].start();
        }

        long total = 0;
        for (int i = 0; i < NUM_THREADS; i++) {
            threads[i].join();
            total += counts[i];
        }

        System.out.println(total);
    }
}
