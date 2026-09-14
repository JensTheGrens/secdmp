#include "array_of_pointers_benchmark.h"

#define nops(n) __asm__ __volatile__(".rept " #n "\n\t" "nop\n\t" ".endr")

/**
 * A benchmark for showing the potential performance benefits of pointer-chasing DMPs
 * 
 * It is a simple array of pointers access and dereference pattern:
 * loop over an array of pointers, dereferencing each element of the array
 */
int array_of_pointers_benchmark(int* array_of_pointers[], int array_len)
{
    unsigned int checksum = 0;
    // follow the pointer and access the value
    for (int i = 0; i < array_len; i++)
    {
        checksum += *(array_of_pointers[i]);
        // do some "work" before loading the next entry
        nops(32);
    }
    return checksum;
}
