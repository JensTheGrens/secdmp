#!/usr/bin/env bash

HACL_CRYPTO_PART_FOLDER=benchmarks/performance/hacl_crypto/build/secret_partitioning
SIM=./ecosystem/simulation/build/sim/partcheck

CRYPTO_BENCHES=(
    "chacha20"
    "salsa20"
    "sha2"
    "hmac"
    "hkdf"
)

for crypto_bench in "${CRYPTO_BENCHES[@]}"; do
    echo Running $crypto_bench
    $SIM $HACL_CRYPTO_PART_FOLDER/$crypto_bench.bin
    echo Finished $crypto_bench
    echo
done
