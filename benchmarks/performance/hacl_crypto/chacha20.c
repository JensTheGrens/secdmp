#include <stdio.h>
#include <inttypes.h>

#include "performance.h"
#include "Hacl_Chacha20.h"
#include "macros.h"

/**
 * "config.h" defines `MODE` (see "macros.h")
 * `MODE` can be:
 * 0 (default)
 * 1 (security_modes for selective disabling)
 * 2 (secret_partitioning for SecDMP and ProSpeCT)
 * 3 (secret_partitioning_no_csr for running the partitioning on processors that don't support writing the region boundaries into CSRs)
 */

#define INPUT_LEN 2048
#define NONCE_LEN 12
#define KEY_LEN 32

static uint8_t nonce[NONCE_LEN] =
{
    0x00, 0x01, 0x02, 0x03,
    0x04, 0x05, 0x06, 0x07,
    0x08, 0x09, 0x0a, 0x0b
};

confidential static uint8_t key[KEY_LEN] =
{
    0x85, 0xd6, 0xbe, 0x78, 0x57, 0x55, 0x6d, 0x33,
    0x7f, 0x44, 0x52, 0xfe, 0x42, 0xd5, 0x06, 0xa8,
    0x01, 0x03, 0x80, 0x8a, 0xfb, 0x0d, 0xb2, 0xfd,
    0x4a, 0xbf, 0xf6, 0xaf, 0x41, 0x49, 0xf5, 0x1b
};

confidential static uint8_t input[] =
    "oDFV2O1aP136YnmEbhZJLMizLukPQF3Ir6kzrYGMOm9M822cFsuLftYMulqTzNwmhvoTkUr7mFwm0r8w2t51ccg2qgRhdWrI5ldwsnRZXoXoogHLUYbNMQPn8Pc4SPVR"
    "ckc1XtQVAoIFSaBrOX3WBl27GZQfqTUROjIrSwlErkwevuIXQfby8WtMRbw8f0RrvJCytHaJfWyD9rC0VMCMFl4gZstTw0WxxBvAEQEhtBdJkJKOEw1xUo9MyiLj77QD"
    "14XSzx2p9wFEpPTbP96X69Mz628IaGgmGbKO06uFesKISWF4qltlIe74Jm00kZpeXCx7uZQ02VGQ3vLPSanJUBv0FYVMbl2VoARBo1D0IAwYvk35fLR4qXUinVgoL8Nx"
    "haaNi6Al6zww23kBSlzXZimSkkG0V9mmjArlOyE5N6DR0C2n9R6jEtsUQejADev21cWPE742mQc8q50u8B5X5QWYiPsZVz4VlMnC0aNDRH7gQMz4gCfuEfd14sm4Kl7T"
    "dNGHw0VzrxaFARKR1T6kih3RgeBCQGYvIJiP9oWQQvXf0WkoL289SrwOYA5lj8ArAH3ftM15K4ih3UrXVfZHvE031bqwTueRZQPTGp7psY5jBNGs5G8bUROxYtUwS63l"
    "kJTj7IuvIUaTIgJvxQHrMUSnN86aG6uMUlNZCFF8lJamsDtLAU5WlXs5aWS2ckwmo0BECJxkZwg8FiPmY2A4EPrmcKnLIj0DHHmbelAV57KmPmRk9q3LeFZeNJvranJU"
    "3FDioc5rSAxT16M5rDlZlxdLANByfz6jaaVa3CcqTGFfS5F0ZHcZlDCEy4fzLQtwDACfQAoiUAOvmfI01q89U1fNqIBcbuXi8AZwcos19bJCpOZfaTkBEldeC2EmTLVL"
    "ZZ6XhZWBJf6iKL2sJriGPfJY6NT67LOit0cvPs8N8o2v9XP7HSRw7RPm5h3GSeVGbcftzQ4VgEefEIlu4QWgoMqRsnASzEhAS0TPk4AUC63ieNwRjwBerK7PA60Oq9ty"
    "RfUfqWXlvCfqV8JOUDo9hzxxopC4Bk0HtjPZ21KyPqQD2AFGVSWcucK4ZL3eYed1R9yG2XWDUfpT5Z8pFNX59X9SAlyjob28IHayBhVmVlmJDFTVS7vcsVqACSetqJCe"
    "xJ8kkBO1eCI1x67LjztTT2N7o4gmb8zunYutnHpIO9OFdVuqv1taRrcCFBhNrhpeBME7n94QQnTK2zJ7grqhEm1ZXLkO235sCIDXnSmkiCsvvNiYEfVyksi3bjZFlNLI"
    "gLorrdR3ykjFWAyJxkotmGCIxLQ1ykGJU8wDLoTnKD21z6IHm9YNl3HNLPEHIzOMdJuYwazUb1ih00RNsr9OYcSPxy7s0xrpt3sJZ44DWtGYwN84OY5eCHhyP2UdiV4O"
    "tlqtbj3seC2yCJ9hznVO67yNHsp07vQgIUXGZSbX5zzTRLrkHrDAVexrKElHrafqRgWwnzibtlvo8cd6jknGbIzXKypEAREYrCzLBusH3A7A8xMc6Gox4JEJxpZ22Ui5"
    "MuFA5fQt9xNwKSJmsZPENe55wjcLg58MWZey8cbiA3LpqK2lPRC7mvBpVvIb0dxDmLTBMuOpCtZw3BBT9HD8YJb7NUUymLK3OhYssk31Cn2a2OoETtyDigEabbaaBbOb"
    "SOQP4w6gZqG6c17JwGLMKqa1L3TdXi4GRIABEr8B0HGEjTTxDDfUMtjZmwyiGp20R4CFxmVoJPPxuk5gTM6yjckL9uQIKyeIeXsyF1PaeMkH7FErgdFEVKYCwbJ0nXIQ"
    "v482eQqwby5gUSlZeQ2Y0IIcXl3c6Noeq41VNV2pljZR9BwPxq9RlLMymTlH7KXh3ckCQ8XhcVfWmpHErV3hwzZiM9qpwCzzxQp1plgbyvx2AVtRSOPm9gbLxncAOMz2"
    "OHPDb6nhAH85wLfCn1n9pREL6NmqO5i7LvA6hOYpDh5QSy24dLsRvc1VvHKfg8VeOZYWWkzxtlv0kUEQ9wYS56E3bmgV49N00fB4CKfnvHRaRag96NbSU8Je9ils3n1i";

confidential static uint8_t ciphertext[INPUT_LEN];
confidential static uint8_t decrypted[INPUT_LEN];

int main()
{
    uint64_t cycles0 = rdcycle();
    initializeSecretRegion();
    setSecurityModeOn();
    Hacl_Chacha20_chacha20_encrypt((uint32_t)INPUT_LEN, ciphertext, input, key, nonce, (uint32_t)0U);
    Hacl_Chacha20_chacha20_decrypt((uint32_t)INPUT_LEN, decrypted, ciphertext, key, nonce, (uint32_t)0U);
    clearRegs();
    setSecurityModeOff();
    uint64_t cycles = rdcycle() - cycles0;

    // printf("Ciphertext: %.*s\n\n", INPUT_LEN, ciphertext);
    // printf("Decrypted: %.*s\n", INPUT_LEN, decrypted);

    printf("Total cycles: %"PRIu64"\n", cycles);

    return 0;
}
