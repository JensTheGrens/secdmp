#pragma once

#include "config.h"

#define clearRegs() __asm__ __volatile__( \
    "li t0, 0\n\t" \
    "li t1, 0\n\t" \
    "li t2, 0\n\t" \
    "li t3, 0\n\t" \
    "li t4, 0\n\t" \
    "li t5, 0\n\t" \
    "li t6, 0\n\t" \
    "li a0, 0\n\t" \
    "li a1, 0\n\t" \
    "li a2, 0\n\t" \
    "li a3, 0\n\t" \
    "li a4, 0\n\t" \
    "li a5, 0\n\t" \
    "li a6, 0\n\t" \
    "li a7, 0\n\t" \
    "li s0, 0\n\t" \
    "li s1, 0\n\t" \
    "li s2, 0\n\t" \
    "li s3, 0\n\t" \
    "li s4, 0\n\t" \
    "li s5, 0\n\t" \
    "li s6, 0\n\t" \
    "li s7, 0\n\t" \
    "li s8, 0\n\t" \
    "li s9, 0\n\t" \
    "li s10, 0\n\t" \
    "li s11, 0" \
    ::: \
    "t0", "t1", "t2", "t3", "t4", "t5", "t6", "a0", "a1", \
    "a2", "a3", "a4", "a5", "a6", "a7", "s0", "s1", "s2", \
    "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11")

// `MODE` can be:
// 0 (default)
// 1 (security_modes for selective disabling)
// 2 (secret_partitioning for SecDMP and ProSpeCT)
// 3 (secret_partitioning_no_csr for running the partitioning on processors that don't support writing the region boundaries into CSRs)

#if MODE == 1
    #define setSecurityModeOff() __asm__ __volatile__("fence\n\t" "csrrwi zero, 0x70b, 0\n\t" "fence")
    #define setSecurityModeOn() __asm__ __volatile__("csrrwi zero, 0x70b, 1\n\t" "fence")
#else
    #define setSecurityModeOff() __asm__ __volatile__("nop\n\t" "nop\n\t" "nop")
    #define setSecurityModeOn() __asm__ __volatile__("nop\n\t" "nop")
#endif

#if MODE == 2 || MODE == 3
    #define confidential __attribute__((section("secret"), aligned(16)))
#else
    #define confidential __attribute__((aligned(16)))
#endif

#if MODE == 2
    #define initializeSecretRegion() \
        extern char *__start_secret; \
        extern char *__stop_secret; \
        __asm__ __volatile__( \
            "csrrw zero, 0x707, %0\n\t" \
            "csrrw zero, 0x708, %1\n\t" \
            "fence" \
            : \
            : "r"(&__start_secret), "r"(&__stop_secret) \
        )
#elif MODE == 3
    // make the memory layouts identical
    #define initializeSecretRegion() \
        extern char *__start_secret; \
        extern char *__stop_secret; \
        __asm__ __volatile__( \
            "add zero, %0, zero\n\t" \
            "add zero, %1, zero\n\t" \
            "nop" \
            : \
            : "r"(&__start_secret), "r"(&__stop_secret) \
        )
#else
    #define initializeSecretRegion()
#endif
