.data
	flushing_array: .space 1024
	boundary: .word 43

.macro setup_secret_region label
#if defined(SECRET_PARTITIONING)
	la t0, \label
	csrrw zero, 0x707, t0
	addi t0, t0, 4
	csrrw zero, 0x708, t0
	fence
#endif
.endm

.macro set_security_mode_off
#if defined(SECURITY_MODES)
	fence
	csrrwi zero, 0x70b, 0
	fence
#endif
.endm

.macro set_security_mode_on
#if defined(SECURITY_MODES)
	csrrwi zero, 0x70b, 1
	fence
#endif
.endm

# ----  Proteus specific macros ----#
.macro terminate_proteus
	lui ra,0x10000
	li sp,4
	sb sp,0(ra)
	.rept 64
	nop
	.endr
.endm

# Flush cache using temporary registers r1 and r2
.macro cflush r1 r2
	la \r1, boundary
	la \r2, flushing_array
loop:
	addi \r2, \r2, 4
	lw zero, (\r2)
	ble \r2, \r1, loop
	.rept 64
	nop
	.endr
.endm

# Load from memory and wait for load to be completed
.macro reload reg addr
	lw \reg, \addr
	.rept 64
	nop
	.endr
.endm
