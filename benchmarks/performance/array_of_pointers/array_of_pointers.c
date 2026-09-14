#include <stdio.h>
#include <stdlib.h>
#include "performance.h"
#include "array_of_pointers_benchmark.h"

#define AOP_LEN 1024

int main()
{
    // init
    int *array_of_pointers[AOP_LEN];
    for (int i = 0; i < AOP_LEN; i++)
    {
        int *ptr = malloc(sizeof(int));
        *ptr = i;

        size_t idx = ((size_t)i * 383 + 57) % AOP_LEN;
        array_of_pointers[idx] = ptr;
    }

    printf("array_of_pointers: %p\n", array_of_pointers);

    // benchmark
    uint64_t begin = rdcycle();
    array_of_pointers_benchmark(array_of_pointers, AOP_LEN);
    uint64_t cycles = rdcycle() - begin;
    printf("Clock cycles: %llu\n", cycles);
}
