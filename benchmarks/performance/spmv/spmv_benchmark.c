#include "spmv_benchmark.h"

/**
 * The SpMV benchmark from HPCG, ported to Proteus
 * See https://github.com/hpcg-benchmark/hpcg/blob/master/src/ComputeSPMV_ref.cpp
 * 
 * SpMV calculates y = Ax with A a sparse matrix
 * matrix_values: an array containing, for each row, the base address of an array with the row's nonzero values
 * matrix_indices: an array containing, for each row, the base address of an array with the column indices of the nonzero values
 * nonzeros_in_row: an array containing, for each row, the number of nonzero elements of that row
 */
void spmv_benchmark(int *matrix_values[], int *matrix_indices[], int nonzeros_in_row[], int rows, int x[], int y[])
{
    for (int i = 0; i < rows; i++)
    {
        int sum = 0;
        const int *const cur_vals = matrix_values[i];
        const int *const cur_inds = matrix_indices[i];
        const int cur_nnz = nonzeros_in_row[i];

        for (int j = 0; j < cur_nnz; j++)
        {
            sum += cur_vals[j] * x[cur_inds[j]];
        }
        y[i] = sum;
    }
}
