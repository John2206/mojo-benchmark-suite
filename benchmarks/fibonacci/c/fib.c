#include <stdio.h>
#include <stdlib.h>

long fib(int n) {
    if (n < 2) return n;
    return fib(n - 1) + fib(n - 2);
}

int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 32;
    if (fib(10) != 55) {
        fprintf(stderr, "self-check failed: fib(10) != 55\n");
        return 1;
    }
    printf("%ld\n", fib(n));
    return 0;
}
