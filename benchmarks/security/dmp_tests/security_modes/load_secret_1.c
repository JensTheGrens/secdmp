#include <stdio.h>

#define setSecurityModeOff() __asm__ __volatile__("csrrwi zero, 0x70b, 0\n\t" "fence")
#define setSecurityModeOn() __asm__ __volatile__("csrrwi zero, 0x70b, 1\n\t" "fence")

#pragma GCC push_options
#pragma GCC optimize("O0")

/**
 * Architecturally Access a secret
 */
int main()
{
    setSecurityModeOn();
    unsigned int secret = 125186138;

    printf("%p\n", &secret);

    secret++;
    secret++;
    setSecurityModeOff();
}

#pragma GCC pop_options
