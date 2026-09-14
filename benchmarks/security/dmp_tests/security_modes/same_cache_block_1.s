# Have public and secret data located together in the same cache block
# selective disabling: the program never actively accesses the secret, so selective disabling never disables the DMP here

.globl _start
.data
    .balign 16 # make sure public starts at a new cache block (1 block contains 4 words = 16 bytes)
    public: .word 1
    secret: .word 125186138

.text
_start:

load_public:
    # load the public data
    la t1, public
    lw t1, 0(t1)

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
