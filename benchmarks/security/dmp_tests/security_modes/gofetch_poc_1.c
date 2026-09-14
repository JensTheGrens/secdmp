#include <stdio.h>

#define nops(n) __asm__ __volatile__(".rept " #n "\n\t" "nop\n\t" ".endr")
#define setSecurityModeOff() __asm__ __volatile__("csrrwi zero, 0x70b, 0\n\t" "fence")
#define setSecurityModeOn() __asm__ __volatile__("csrrwi zero, 0x70b, 1\n\t" "fence")

#pragma GCC push_options
#pragma GCC optimize("O0")

/**
 * (Configured for processor: delay 64, cache 16 sets 4 ways, 32 rob entries
 * 
 * Execute the GoFetch attack on OpenSSL's CT conditional swap to verify the leakage of DMPs
 * This function simulates the attack by alternating between attacker and victim roles.
 * For simplicity, we assume the attacker-chosen pointer is part of shared memory
 * 
 * Secret is either 0x00 or 0xff ("0" or "1")
 * The swap only occurs when secret is 1
 * 
 * The attack works like this:
 * B contains a pointer, A doesn't.
 * secret = 1: A contains the pointer -> DMP prefetches it in step 4
 * secret = 0: A contains no pointer -> no prefetch occurs in step 4
 * this difference in the microarchitecture will be detected by the noninterference script
 */
int main()
{
    setSecurityModeOn();
    // secret = '\xff';
    unsigned char secret;
    __asm__ __volatile__(
        "li %0, -1"
        : "=r"(secret)
    );
    setSecurityModeOff();
    
    // Step 1: attacker sends inputs to the victim
    // The attacker puts a pointer in array B but not in A
    unsigned char a[] = {'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'C', 'C', 'C', 'C', 'D', 'D', 'D', 'D'};
    unsigned char b[] = {0x00, 0x00, 0x01, 0x90, 'B', 'B', 'B', 'B', 'C', 'C', 'C', 'C', 'D', 'D', 'D', 'D'};

    // printing the address of array A
    printf("%p\n", a);

    // Step 2: victim performs the conditional CT swap
    setSecurityModeOn();
    unsigned char tmp;
    for (size_t i = 0; i < 16; i++)
    {
        tmp = a[i] ^ b[i];
        tmp &= secret;
        a[i] ^= tmp;
        b[i] ^= tmp;
    }
    setSecurityModeOff();

    // Step 3: attacker 'flushes' the cache right before victim accesses array A
    // Proteus has no flush, so instead evict the array with the pointer (array A),
    // and the pointer itself
    nops(32);
    __asm__ __volatile__(
        // t0 = 0x80000000 = 10000000000000000000000000000000 = set 0 0 0 0
        "lui t0, 0x80000\n\t"

        // 1. evict the pointer
        "lw x0, 0(t0)\n\t"
        "lw x0, 256(t0)\n\t" // 2^8
        "lw x0, 512(t0)\n\t" // 2^9
        "lw x0, 768(t0)\n\t" // 2^8 + 2^9

        // 2. evict array A = 0x90012b88 = 10010000000000010010101110001000 = set 1 0 0 0
        "lw x0, 128(t0)\n\t" // 2^7
        "lw x0, 384(t0)\n\t" // 2^7 + 2^8
        "lw x0, 640(t0)\n\t" // 2^7 + 2^9
        "lw x0, 896(t0)\n\t" // 2^7 + 2^8 + 2^9
        
        ::: "t0"
    );
    nops(32);

    // Step 4: victim accesses array A, loading it back into the cache
    setSecurityModeOn();
    char x = a[0];
    nops(64);
    setSecurityModeOff();
}

#pragma GCC pop_options
