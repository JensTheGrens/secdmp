#pragma once

#define WORK_PERCENTAGE 90
#define CRYPTO_BENCH 4
#define WORK_BENCH 3
#define DMP 3

// selected crypto benchmark
#if CRYPTO_BENCH == 0
    #define CRYPTO_BENCH_NAME "chacha20"
#elif CRYPTO_BENCH == 1
    #define CRYPTO_BENCH_NAME "salsa20"
#elif CRYPTO_BENCH == 2
    #define CRYPTO_BENCH_NAME "sha2"
#elif CRYPTO_BENCH == 3
    #define CRYPTO_BENCH_NAME "hmac"
#elif CRYPTO_BENCH == 4
    #define CRYPTO_BENCH_NAME "hkdf"
#endif

// selected work benchmark
#if WORK_BENCH == 0
    #define WORK_BENCH_NAME "sglib-combined"
#elif WORK_BENCH == 1
    #define WORK_BENCH_NAME "coremark"
#elif WORK_BENCH == 2
    #define WORK_BENCH_NAME "array_of_pointers"
#elif WORK_BENCH == 3
    #define WORK_BENCH_NAME "spmv"
#endif

// selected dmp
#if DMP == 0
    #define DMP_NAME "AppleDmp"
#elif DMP == 1
    #define DMP_NAME "IntelDmp"
#elif DMP == 2
    #define DMP_NAME "Cdp"
#elif DMP == 3
    #define DMP_NAME "Imp"
#endif

// calculate work and crypto iterations
#define CRYPTO_PERCENTAGE (100-WORK_PERCENTAGE)

#if WORK_PERCENTAGE > CRYPTO_PERCENTAGE
    #define WORK_SCALING ((double)WORK_PERCENTAGE/CRYPTO_PERCENTAGE)
    #define CRYPTO_SCALING 1
#else
    #define WORK_SCALING 1
    #define CRYPTO_SCALING ((double)CRYPTO_PERCENTAGE/WORK_PERCENTAGE)
#endif

#if DMP == 0
    #if CRYPTO_BENCH == 0
        #define BASELINE_CRYPTO_CYCLES 28287
    #elif CRYPTO_BENCH == 1
        #define BASELINE_CRYPTO_CYCLES 26472
    #elif CRYPTO_BENCH == 2
        #define BASELINE_CRYPTO_CYCLES 31473
    #elif CRYPTO_BENCH == 3
        #define BASELINE_CRYPTO_CYCLES 64642
    #elif CRYPTO_BENCH == 4
        #define BASELINE_CRYPTO_CYCLES 109685
    #endif
    #if WORK_BENCH == 0
        #define BASELINE_WORK_CYCLES 384589
    #elif WORK_BENCH == 1
        #define BASELINE_WORK_CYCLES 953716
    #elif WORK_BENCH == 2
        #define BASELINE_WORK_CYCLES 67838
    #elif WORK_BENCH == 3
        #define BASELINE_WORK_CYCLES 1586618
    #endif
#elif DMP == 1
    #if CRYPTO_BENCH == 0
        #define BASELINE_CRYPTO_CYCLES 28286
    #elif CRYPTO_BENCH == 1
        #define BASELINE_CRYPTO_CYCLES 26932
    #elif CRYPTO_BENCH == 2
        #define BASELINE_CRYPTO_CYCLES 31858
    #elif CRYPTO_BENCH == 3
        #define BASELINE_CRYPTO_CYCLES 65658
    #elif CRYPTO_BENCH == 4
        #define BASELINE_CRYPTO_CYCLES 111340
    #endif
    #if WORK_BENCH == 0
        #define BASELINE_WORK_CYCLES 410065
    #elif WORK_BENCH == 1
        #define BASELINE_WORK_CYCLES 1136560
    #elif WORK_BENCH == 2
        #define BASELINE_WORK_CYCLES 57680
    #elif WORK_BENCH == 3
        #define BASELINE_WORK_CYCLES 1586729
    #endif
#elif DMP == 2
    #if CRYPTO_BENCH == 0
        #define BASELINE_CRYPTO_CYCLES 28290
    #elif CRYPTO_BENCH == 1
        #define BASELINE_CRYPTO_CYCLES 26438
    #elif CRYPTO_BENCH == 2
        #define BASELINE_CRYPTO_CYCLES 31442
    #elif CRYPTO_BENCH == 3
        #define BASELINE_CRYPTO_CYCLES 64528
    #elif CRYPTO_BENCH == 4
        #define BASELINE_CRYPTO_CYCLES 109827
    #endif
    #if WORK_BENCH == 0
        #define BASELINE_WORK_CYCLES 385299
    #elif WORK_BENCH == 1
        #define BASELINE_WORK_CYCLES 944307
    #elif WORK_BENCH == 2
        #define BASELINE_WORK_CYCLES 67898
    #elif WORK_BENCH == 3
        #define BASELINE_WORK_CYCLES 1583378
    #endif
#elif DMP == 3
    #if CRYPTO_BENCH == 0
        #define BASELINE_CRYPTO_CYCLES 28289
    #elif CRYPTO_BENCH == 1
        #define BASELINE_CRYPTO_CYCLES 26905
    #elif CRYPTO_BENCH == 2
        #define BASELINE_CRYPTO_CYCLES 31858
    #elif CRYPTO_BENCH == 3
        #define BASELINE_CRYPTO_CYCLES 65663
    #elif CRYPTO_BENCH == 4
        #define BASELINE_CRYPTO_CYCLES 111318
    #endif
    #if WORK_BENCH == 0
        #define BASELINE_WORK_CYCLES 409900
    #elif WORK_BENCH == 1
        #define BASELINE_WORK_CYCLES 1137624
    #elif WORK_BENCH == 2
        #define BASELINE_WORK_CYCLES 95564
    #elif WORK_BENCH == 3
        #define BASELINE_WORK_CYCLES 1310538
    #endif
#endif

#if BASELINE_WORK_CYCLES > BASELINE_CRYPTO_CYCLES
    #define CRYPTO_SCALE_FACTOR ((double)BASELINE_WORK_CYCLES/BASELINE_CRYPTO_CYCLES)
    #define WORK_SCALE_FACTOR 1
#else
    #define CRYPTO_SCALE_FACTOR 1
    #define WORK_SCALE_FACTOR ((double)BASELINE_CRYPTO_CYCLES/BASELINE_WORK_CYCLES)
#endif

#define WORK_ITERATIONS (WORK_SCALE_FACTOR*WORK_SCALING + 0.5)
#define CRYPTO_ITERATIONS (CRYPTO_SCALE_FACTOR*CRYPTO_SCALING + 0.5)
