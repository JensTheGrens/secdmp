#ifndef ARRAY_OF_POINTERS_BENCHMARK_H
#define ARRAY_OF_POINTERS_BENCHMARK_H

/**
 * A benchmark for showing the potential performance benefits of pointer-chasing DMPs
 * 
 * It is a simple array of pointers access and dereference pattern:
 * loop over an array of pointers, dereferencing each element of the array
 */
int array_of_pointers_benchmark(int* array_of_pointers[], int array_len);

#endif
