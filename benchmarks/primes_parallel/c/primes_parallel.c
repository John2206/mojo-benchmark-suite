#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#define NUM_THREADS 4

typedef struct {
    long start, end;
    long count;
} ThreadArg;

int is_prime(long x) {
    if (x < 2) return 0;
    if (x % 2 == 0) return x == 2;
    for (long d = 3; d * d <= x; d += 2) {
        if (x % d == 0) return 0;
    }
    return 1;
}

void *worker(void *arg) {
    ThreadArg *t = (ThreadArg *)arg;
    long count = 0;
    for (long x = t->start; x < t->end; x++) {
        if (is_prime(x)) count++;
    }
    t->count = count;
    return NULL;
}

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 2000000;

    if (!is_prime(2) || !is_prime(97) || is_prime(100) || is_prime(1)) {
        fprintf(stderr, "self-check failed: is_prime disagrees with known facts\n");
        return 1;
    }

    pthread_t threads[NUM_THREADS];
    ThreadArg args[NUM_THREADS];
    long chunk = n / NUM_THREADS;
    for (int i = 0; i < NUM_THREADS; i++) {
        args[i].start = i * chunk;
        if (args[i].start < 2) args[i].start = 2;
        args[i].end = (i == NUM_THREADS - 1) ? n : (i + 1) * chunk;
        pthread_create(&threads[i], NULL, worker, &args[i]);
    }

    long total = 0;
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
        total += args[i].count;
    }

    printf("%ld\n", total);
    return 0;
}
