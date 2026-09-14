#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>

#include "performance.h"
#include "../hacl_crypto/macros.h"
#include "bench_config.h"

/**
 * This file provides the DMP-Bench benchmark for SecDMP, splitting execution into two sections:
 * 
 * 1. Work: executes a public workload which has a performance increase from DMPs; the workload depends on the configuration:
 *  - 0: sglib-combined
 *  - 1: coremark
 *  - 2: array_of_pointers
 *  - 3: spmv
 * 
 * 2. Crypto: runs a HACL* crypto benchmark on secret data; the crypto primitive depends on the configuration:
 *  - 0: chacha20
 *  - 1: salsa20
 *  - 2: sha2
 *  - 3: hmac
 *  - 4: hkdf
 *
 * "bench_config.h" defines `WORK_PERCENTAGE`, `CRYPTO_BENCH`, `WORK_BENCH` and `DMP`
 * "../hacl_crypto/config.h" defines `MODE` (see ../hacl_crypto/macros.h)
 * 
 * `WORK_PERCENTAGE` defines the percentage of time the program spends working
 * `CRYPTO_BENCH` and `WORK_BENCH` define the used work and crypto benchmarks
 * `DMP` defines which DMP is used, which impacts the calculation of `WORK_ITERATIONS` and `CRYPTO_ITERATIONS` to get the desired `WORK_PERCENTAGE`
 * (because depending on the DMP, the selected `CRYPTO_BENCH` and `WORK_BENCH` take a different number of cycles)
 * `MODE` can be:
 * 0 (default)
 * 1 (security_modes for selective disabling)
 * 2 (secret_partitioning for SecDMP and ProSpeCT)
 * 3 (secret_partitioning_no_csr for running the partitioning on processors that don't support writing the region boundaries into CSRs)
 *
 * This program thus contains a public section that increases in performance from DMPs and a secret section,
 * with as purpose to evaluate the performance of DMP defenses for programs that need to protect secrets
 */

#if WORK_BENCH == 0
    #include "support.h"
#elif WORK_BENCH == 1
    #include "coremark_driver.h"
#elif WORK_BENCH == 2
    #include "array_of_pointers_benchmark.h"
    #define AOP_LEN 1024
#elif WORK_BENCH == 3
    #include "spmv_benchmark.h"
    #define ROWS 1024
    #define NONZEROS_PER_ROW 32
    #define NONZEROS (ROWS * NONZEROS_PER_ROW)
    #define COLS 1024
#endif

#define TOTAL_INPUT_LEN 2048
#define INPUT_LEN 128
#define INPUT_BLOCKS (TOTAL_INPUT_LEN / INPUT_LEN)
#define INPUT_BLOCK(i) (input + ((i) % INPUT_BLOCKS) * INPUT_LEN)

confidential static uint8_t input[] =
    "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";

#if CRYPTO_BENCH == 0
    #include "Hacl_Chacha20.h"
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
    confidential static uint8_t ciphertext[INPUT_LEN];
    confidential static uint8_t decrypted[INPUT_LEN];
#elif CRYPTO_BENCH == 1
    #include "Hacl_Salsa20.h"
    #define NONCE_LEN 8
    #define KEY_LEN 32
    static uint8_t nonce[NONCE_LEN] =
    {
        0x00, 0x01, 0x02, 0x03,
        0x04, 0x05, 0x06, 0x07
    };
    confidential static uint8_t key[KEY_LEN] =
    {
        0x85, 0xd6, 0xbe, 0x78, 0x57, 0x55, 0x6d, 0x33,
        0x7f, 0x44, 0x52, 0xfe, 0x42, 0xd5, 0x06, 0xa8,
        0x01, 0x03, 0x80, 0x8a, 0xfb, 0x0d, 0xb2, 0xfd,
        0x4a, 0xbf, 0xf6, 0xaf, 0x41, 0x49, 0xf5, 0x1b
    };
    confidential static uint8_t ciphertext[INPUT_LEN];
    confidential static uint8_t decrypted[INPUT_LEN];
#elif CRYPTO_BENCH == 2
    #include "Hacl_Hash_SHA2.h"
    #define HASH_LEN 32
    confidential static uint8_t hash[HASH_LEN];
#elif CRYPTO_BENCH == 3
    #include "Hacl_HMAC.h"
    #define KEY_LEN 32
    #define MAC_LEN 32
    confidential static uint8_t key[KEY_LEN] =
    {
        0x85, 0xd6, 0xbe, 0x78, 0x57, 0x55, 0x6d, 0x33,
        0x7f, 0x44, 0x52, 0xfe, 0x42, 0xd5, 0x06, 0xa8,
        0x01, 0x03, 0x80, 0x8a, 0xfb, 0x0d, 0xb2, 0xfd,
        0x4a, 0xbf, 0xf6, 0xaf, 0x41, 0x49, 0xf5, 0x1b
    };
    confidential static uint8_t mac[MAC_LEN];
#elif CRYPTO_BENCH == 4
    #include "Hacl_HKDF.h"
    #define SALT_LEN 8
    #define INFO_LEN 8
    #define PR_KEY_LEN 32
    #define OUT_KEY_LEN 32
    static uint8_t salt[SALT_LEN] =
    {
        0x00, 0x01, 0x02, 0x03,
        0x04, 0x05, 0x06, 0x07
    };
    static uint8_t info[INFO_LEN] =
    {
        0x08, 0x09, 0x0a, 0x0b,
        0x0c, 0x0d, 0x0e, 0x0f
    };
    confidential static uint8_t pr_key[PR_KEY_LEN];
    confidential static uint8_t output_key[OUT_KEY_LEN];
#endif

static volatile int work_iterations_init = (int)WORK_ITERATIONS;
static volatile int crypto_iterations_init = (int)CRYPTO_ITERATIONS;

int main()
{
    initializeSecretRegion();

    // initialize work
    #if WORK_BENCH == 0
    #elif WORK_BENCH == 1
       initialise_benchmark();
    #elif WORK_BENCH == 2
        int *array_of_pointers[AOP_LEN];
        for (int i = 0; i < AOP_LEN; i++)
        {
            int *ptr = malloc(sizeof(int));
            *ptr = i;

            size_t idx = ((size_t)i * 383 + 57) % AOP_LEN;
            array_of_pointers[idx] = ptr;
        }
    #elif WORK_BENCH == 3
        int *matrix_values[ROWS];
        int *matrix_indices[ROWS];
        int nonzeros_in_row[ROWS];
        int values[NONZEROS];
        int indices[NONZEROS];
        int x[COLS];
        int y[ROWS];
        unsigned int state = 12345;
        for (int i = 0; i < ROWS; i++)
        {
            matrix_values[i] = &values[i * NONZEROS_PER_ROW];
            matrix_indices[i] = &indices[i * NONZEROS_PER_ROW];
            nonzeros_in_row[i] = NONZEROS_PER_ROW;
            for (int j = 0; j < nonzeros_in_row[i]; j++)
            {
                state = state * 1664525u + 1013904223u;
                matrix_indices[i][j] = (int)((state >> 16) % COLS);
                state = state * 1664525u + 1013904223u;
                matrix_values[i][j] = (int)(1 + ((state >> 16) & 0xFF));
            }
        }
        for (int i = 0; i < COLS; i++)
        {
            x[i] = i;
        }
    #endif

    uint64_t cycles0, cycles, work_cycles, encrypt_cycles;

    work_cycles = 0;
    encrypt_cycles = 0;

    const int work_iterations = work_iterations_init;
    const int crypto_iterations = crypto_iterations_init;

    // work
    cycles0 = rdcycle();
    for (int i = 0; i < work_iterations; i++)
    {
        #if WORK_BENCH == 0
            benchmark(); // sglib-combined
        #elif WORK_BENCH == 1
            benchmark(); // coremark (different #include)
        #elif WORK_BENCH == 2
            array_of_pointers_benchmark(array_of_pointers, AOP_LEN);
        #elif WORK_BENCH == 3
            spmv_benchmark(matrix_values, matrix_indices, nonzeros_in_row, ROWS, x, y);
        #endif
    }
    cycles = rdcycle() - cycles0;
    work_cycles += cycles;

    // encrypt
    cycles0 = rdcycle();
    setSecurityModeOn();
    for (int i = 0; i < crypto_iterations; i++)
    {
        #if CRYPTO_BENCH == 0
            Hacl_Chacha20_chacha20_encrypt((uint32_t)INPUT_LEN, ciphertext, INPUT_BLOCK(i), key, nonce, (uint32_t)0U);
            Hacl_Chacha20_chacha20_decrypt((uint32_t)INPUT_LEN, decrypted, ciphertext, key, nonce, (uint32_t)0U);
        #elif CRYPTO_BENCH == 1
            Hacl_Salsa20_salsa20_encrypt((uint32_t)INPUT_LEN, ciphertext, INPUT_BLOCK(i), key, nonce, (uint32_t)0U);
            Hacl_Salsa20_salsa20_decrypt((uint32_t)INPUT_LEN, decrypted, ciphertext, key, nonce, (uint32_t)0U);
        #elif CRYPTO_BENCH == 2
            Hacl_Hash_SHA2_hash_256(INPUT_BLOCK(i), (uint32_t)INPUT_LEN, hash);
        #elif CRYPTO_BENCH == 3
            Hacl_HMAC_compute_sha2_256(mac, key, (uint32_t)KEY_LEN, INPUT_BLOCK(i), (uint32_t)INPUT_LEN);
        #elif CRYPTO_BENCH == 4
            Hacl_HKDF_extract_sha2_256(pr_key, salt, (uint32_t)SALT_LEN, INPUT_BLOCK(i), (uint32_t)INPUT_LEN);
            Hacl_HKDF_expand_sha2_256(output_key, pr_key, (uint32_t)PR_KEY_LEN, info, (uint32_t)INFO_LEN, (uint32_t)OUT_KEY_LEN);
        #endif
    }
    clearRegs();
    setSecurityModeOff();
    cycles = rdcycle() - cycles0;
    encrypt_cycles += cycles;

    // finish
    printf("Work cycles   :[%llu]\n", work_cycles);
    printf("Encrypt cycles:[%llu]\n", encrypt_cycles);
    printf("Total cycles  :[%llu]\n", work_cycles + encrypt_cycles);

    return 0;
}
