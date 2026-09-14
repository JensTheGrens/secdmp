#include <stdio.h>
#include "performance.h"
#include "coremark_driver.h"

int main()
{
    // init
    initialise_benchmark();

    // benchmark
    uint64_t begin = rdcycle();
    int result = benchmark();
    uint64_t cycles = rdcycle() - begin;
    printf("Clock cycles: %llu\n", cycles);

    printf("RET=%d\n", !verify_benchmark(result));
}
