# Recursive prefetching leakage test

.globl _start
.data
    pointer: .word 0
    .balign 16 # one separate cache block for the secret (1 block contains 4 words = 16 bytes)
    secret: .word 0x800023cf, 0, 0 ,0

.text
_start:

setup:
    # secret partitioning:
    # lower boundary = &secret
    # upper boundary = &secret + 4
    la t0, secret
    csrrw zero, 0x707, t0
    addi t0, t0, 4
    csrrw zero, 0x708, t0
    fence

    # pointer = &secret
    la t0, pointer
    la t1, secret
    sw t1, 0(t0)

load_public:
    # load the public pointer that points to the secret
    lw t0, 0(t0)

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
