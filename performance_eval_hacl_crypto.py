#!/usr/bin/env python3

import subprocess
import re
import os

SIM_BUILD_FOLDER = "ecosystem/simulation/build/sim"
BENCH_BUILD_FOLDER = "benchmarks/performance/hacl_crypto/build"

DMPs = [
    "AppleDmp",
    "IntelDmp",
    "Cdp",
    "Imp"
]

PROCESSOR_CONFIGS = {
    "proteus_dmp": "default",
    "permanent_disabling": "default",
    "selective_disabling": "security_modes",
    "partitioning": "secret_partitioning_no_csr",
    "secdmp": "secret_partitioning",
    "prospect": "secret_partitioning",
    "prospect_secdmp": "secret_partitioning",
}

CRYPTO_BENCHES = [
    "chacha20",
    "salsa20",
    "sha2",
    "hmac",
    "hkdf",
]

def run_simulation(dmp, sim, folder, crypto_bench):
    sim_file = sim if sim != "partitioning" else "proteus_dmp"
    return {
        'process': subprocess.Popen(['stdbuf', '-o0'] + [f"{SIM_BUILD_FOLDER}/{dmp}/{sim_file}", f"{BENCH_BUILD_FOLDER}/{folder}/{crypto_bench}.bin"], bufsize=1, stdout=subprocess.PIPE, encoding="utf8"),
        'sim': sim,
        'crypto_bench': crypto_bench,
        'folder': folder
    }

results = {
    'chacha20': {
        'proteus_dmp': 0,
        'permanent_disabling': 0,
        'selective_disabling': 0,
        'partitioning': 0,
        'secdmp': 0,
        'prospect': 0,
        'prospect_secdmp': 0,
    },
    'salsa20': {
        'proteus_dmp': 0,
        'permanent_disabling': 0,
        'selective_disabling': 0,
        'partitioning': 0,
        'secdmp': 0,
        'prospect': 0,
        'prospect_secdmp': 0,
    },
    'sha2': {
        'proteus_dmp': 0,
        'permanent_disabling': 0,
        'selective_disabling': 0,
        'partitioning': 0,
        'secdmp': 0,
        'prospect': 0,
        'prospect_secdmp': 0,
    },
    'hmac': {
        'proteus_dmp': 0,
        'permanent_disabling': 0,
        'selective_disabling': 0,
        'partitioning': 0,
        'secdmp': 0,
        'prospect': 0,
        'prospect_secdmp': 0,
    },
    'hkdf': {
        'proteus_dmp': 0,
        'permanent_disabling': 0,
        'selective_disabling': 0,
        'partitioning': 0,
        'secdmp': 0,
        'prospect': 0,
        'prospect_secdmp': 0,
    }
}

def calculate_relative_results(key, crypto_bench):
    result = round((results[crypto_bench][key] - results[crypto_bench]["proteus_dmp"]) / results[crypto_bench]["proteus_dmp"] * 100, 1)
    if str(result)[0] == '-':
        return str(result) + '%'
    else:
        return '+' + str(result) + '%'


def main():
    for dmp_idx in range(len(DMPs)):
        dmp = DMPs[dmp_idx]
        print("-"*85 + "\n")
        print(f"Part {dmp_idx + 1}: {dmp}:\n")

        processes = []

        for crypto_bench in CRYPTO_BENCHES:
            for sim, folder in PROCESSOR_CONFIGS.items():
                processes.append(run_simulation(dmp, sim, folder, crypto_bench))

        os.makedirs(f"results/performance_evaluation/hacl_crypto/{dmp}", exist_ok=True)
        for proc in processes:
            for line in iter(proc['process'].stdout.readline, ''):
                match = re.match(r"Total cycles\s*:\s*(\d+)", line)
                if match:
                    results[proc['crypto_bench']][proc['sim']] = int(match.group(1))

        for crypto_bench in CRYPTO_BENCHES:
            summary = f"{crypto_bench}:\n"
            for sim in PROCESSOR_CONFIGS.keys():
                if sim == "proteus_dmp":
                    summary += ("{:<25} {:<8}\n".format(
                        sim,
                        str(results[crypto_bench][sim])))
                else:
                    summary += ("{:<25} {:<8} {:<40}\n".format(
                        sim,
                        str(results[crypto_bench][sim]),
                        f"({calculate_relative_results(sim, crypto_bench)})"))
            print(summary)
            print("-"*85)
            print()

            with open(f"results/performance_evaluation/hacl_crypto/{dmp}/{crypto_bench}.txt", 'w') as logfile:
                logfile.write(summary)

if __name__ == "__main__":
    main()
