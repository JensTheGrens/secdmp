#include <stdio.h>
#include <stdlib.h>
#include "performance.h"
#include "spmv_benchmark.h"

#define ROWS 1024
#define NONZEROS_PER_ROW 32
#define NONZEROS (ROWS * NONZEROS_PER_ROW)
#define COLS 1024

int main()
{
    // init
    int *matrix_values[ROWS];
    int *matrix_indices[ROWS];
    int nonzeros_in_row[ROWS];
    int values[NONZEROS];
    int indices[NONZEROS];
    int x[COLS];
    int y[ROWS];
    unsigned int state = 12345;
    for (int i = 0; i < ROWS; i++)
    {
        matrix_values[i] = &values[i * NONZEROS_PER_ROW];
        matrix_indices[i] = &indices[i * NONZEROS_PER_ROW];
        nonzeros_in_row[i] = NONZEROS_PER_ROW;
        for (int j = 0; j < nonzeros_in_row[i]; j++)
        {
            state = state * 1664525u + 1013904223u;
            matrix_indices[i][j] = (int)((state >> 16) % COLS);
            state = state * 1664525u + 1013904223u;
            matrix_values[i][j] = (int)(1 + ((state >> 16) & 0xFF));
        }
    }
    for (int i = 0; i < COLS; i++)
    {
        x[i] = i;
    }

    printf("indices: %p\n", indices);
    printf("x: %p\n", x);

    // benchmark
    uint64_t begin = rdcycle();
    spmv_benchmark(matrix_values, matrix_indices, nonzeros_in_row, ROWS, x, y);
    uint64_t cycles = rdcycle() - begin;
    printf("Clock cycles: %llu\n", cycles);
}
