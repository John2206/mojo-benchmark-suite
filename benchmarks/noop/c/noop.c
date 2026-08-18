#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 0;
    (void)n;
    printf("0\n");
    return 0;
}
