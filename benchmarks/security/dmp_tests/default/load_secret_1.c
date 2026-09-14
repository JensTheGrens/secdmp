#include <stdio.h>

#pragma GCC push_options
#pragma GCC optimize("O0")

/**
 * Architecturally Access a secret
 */
int main()
{
    unsigned int secret = 125186138;

    printf("%p\n", &secret);

    secret++;
    secret++;
}

#pragma GCC pop_options
