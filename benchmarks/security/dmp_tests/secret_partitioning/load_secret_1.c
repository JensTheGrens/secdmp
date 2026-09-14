#include <stdio.h>

#define confidential __attribute__((section("secret"))) static

#pragma GCC push_options
#pragma GCC optimize("O0")

extern char *__start_secret;
extern char *__stop_secret;

/**
 * Architecturally Access a secret
 */
int main()
{
    // set the secret region
    __asm__ __volatile__(
        "csrrw zero, 0x707, %0\n\t"
        "csrrw zero, 0x708, %1\n\t"
        "fence\n\t"
        :
        : "r"(&__start_secret), "r"(&__stop_secret)
    );

    confidential unsigned int secret = 125186138;

    printf("%p\n", &secret);

    secret++;
    secret++;
}

#pragma GCC pop_options
