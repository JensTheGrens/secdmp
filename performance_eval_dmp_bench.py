#!/usr/bin/env python3

import subprocess
import re
import os

SIM_BUILD_FOLDER = "ecosystem/simulation/build/sim"
BENCH_BUILD_FOLDER = "benchmarks/performance/dmp_bench/build"

PROCESSOR_CONFIGS = {
    "proteus_dmp": "default",
    "permanent_disabling": "default",
    "selective_disabling": "security_modes",
    "partitioning": "secret_partitioning_no_csr",
    "secdmp": "secret_partitioning",
    "prospect": "secret_partitioning",
    "prospect_secdmp": "secret_partitioning",
}

WORK_PERCENTAGES = [
    "25",
    "50",
    "75",
    "90",
]

CRYPTO_BENCHES = {
    "0": "chacha20",
    "1": "salsa20",
    "2": "sha2",
    "3": "hmac",
    "4": "hkdf",
}

WORK_BENCHES = {
    "0": "sglib-combined",
    "1": "coremark",
    "2": "array_of_pointers",
    "3": "spmv",
}

DMPS = {
    "0": "AppleDmp",
    "1": "IntelDmp",
    "2": "Cdp",
    "3": "Imp",
}

def run_simulation(sim, folder, dmp, crypto_bench, work_bench, work_p):
    # print(f"Running {work_p}% work on {sim}...")
    sim_file = sim if sim != "partitioning" else "proteus_dmp"
    return {
        'process': subprocess.Popen(['stdbuf', '-o0'] + [f"{SIM_BUILD_FOLDER}/{DMPS[dmp]}/{sim_file}", f"{BENCH_BUILD_FOLDER}/dmp{dmp}/{folder}/crypto{crypto_bench}_work{work_bench}_p{work_p}.bin"], bufsize=1, stdout=subprocess.PIPE, encoding="utf8"),
        'sim': sim,
        'work_p': work_p
    }

results = {
    'proteus_dmp': {
        '25': 0,
        '50': 0,
        '75': 0,
        '90': 0,
    },
    'permanent_disabling': {
        '25': 0,
        '50': 0,
        '75': 0,
        '90': 0,
    },
    'selective_disabling': {
        '25': 0,
        '50': 0,
        '75': 0,
        '90': 0,
    },
    'partitioning': {
        '25': 0,
        '50': 0,
        '75': 0,
        '90': 0,
    },
    'secdmp': {
        '25': 0,
        '50': 0,
        '75': 0,
        '90': 0,
    },
    'prospect': {
        '25': 0,
        '50': 0,
        '75': 0,
        '90': 0,
    },
    'prospect_secdmp': {
        '25': 0,
        '50': 0,
        '75': 0,
        '90': 0,
    },
}

def print_work_percentage(sim, work_p, work_cycles, encrypt_cycles):
    actual = work_cycles / (work_cycles + encrypt_cycles) * 100
    print(f"({sim}) expected: {work_p}% actual: {actual:.1f}%")


def calculate_relative_results(key, work_p):
    result = round((results[key][work_p] - results['proteus_dmp'][work_p]) / results['proteus_dmp'][work_p] * 100, 1)
    if str(result)[0] == '-':
        return str(result) + '%'
    else:
        return '+' + str(result) + '%'
    

def main():
    progress = 0
    for crypto_bench, crypto_bench_name in CRYPTO_BENCHES.items():
        for work_bench, work_bench_name in WORK_BENCHES.items():
            for dmp, dmp_name in DMPS.items():
                progress = progress+1
                print("\n" + "-" * 100)

                print("{:<17} {:<14} {:<16} {:<23}\n".format(
                    f"[progress: {progress}/{len(CRYPTO_BENCHES)*len(WORK_BENCHES)*len(DMPS)}]",
                    f"dmp={dmp_name}",
                    f"crypto={crypto_bench_name}",
                    f"work={work_bench_name}"
                ))

                processes = []

                for sim, folder in PROCESSOR_CONFIGS.items():
                    for work_p in WORK_PERCENTAGES:
                        processes.append(run_simulation(sim, folder, dmp, crypto_bench, work_bench, work_p))

                i = 1

                print("Verifying work percentages:\n")

                os.makedirs(f"results/performance_evaluation/dmp_bench/{dmp_name}", exist_ok=True)
                with open(f"results/performance_evaluation/dmp_bench/{dmp_name}/dmp_bench_{crypto_bench_name}_{work_bench_name}.txt", 'w') as logfile:
                    for proc in processes:
                        logfile.write(f"{i}. {proc['sim']} with work_p {proc['work_p']}:\n")
                        logfile.write(f"{'-' * 80}\n")
                        i += 1
                        work_cycles = None
                        encrypt_cycles = None
                        for line in iter(proc['process'].stdout.readline, ''):
                            logfile.write(line)
                            match = re.match(r"Total cycles\s*:\[(\d+)\]", line)
                            if match:
                                results[proc['sim']][proc['work_p']] = int(match.group(1))
                            match = re.match(r"Work cycles\s*:\[(\d+)\]", line)
                            if match:
                                work_cycles = int(match.group(1))
                            match = re.match(r"Encrypt cycles\s*:\[(\d+)\]", line)
                            if match:
                                encrypt_cycles = int(match.group(1))
                        if proc['sim'] == "proteus_dmp":
                            print_work_percentage(proc['sim'], proc['work_p'], work_cycles, encrypt_cycles)
                        # print(f"\nFinished {proc['work_p']}% work on {proc['sim']}", flush=True, end="")
                        logfile.write("\n")

                print()
                print()

                summary = "Summary:\n{:<25} {:<18} {:<18} {:<18} {:<18}\n".format("", "25% W", "50% W", "75% W", "90% W")
                for sim in PROCESSOR_CONFIGS.keys():
                    if sim == "proteus_dmp":
                        summary += ("{:<25} {:<18} {:<18} {:<18} {:<18}\n"
                            .format(sim,
                                    str(results[sim][WORK_PERCENTAGES[0]]),
                                    str(results[sim][WORK_PERCENTAGES[1]]),
                                    str(results[sim][WORK_PERCENTAGES[2]]),
                                    str(results[sim][WORK_PERCENTAGES[3]])))
                    else:
                        summary += ("{:<25} {:<18} {:<18} {:<18} {:<18}\n"
                            .format(sim,
                                    str(results[sim][WORK_PERCENTAGES[0]]) + f" ({calculate_relative_results(sim, WORK_PERCENTAGES[0])})",
                                    str(results[sim][WORK_PERCENTAGES[1]]) + f" ({calculate_relative_results(sim, WORK_PERCENTAGES[1])})",
                                    str(results[sim][WORK_PERCENTAGES[2]]) + f" ({calculate_relative_results(sim, WORK_PERCENTAGES[2])})",
                                    str(results[sim][WORK_PERCENTAGES[3]]) + f" ({calculate_relative_results(sim, WORK_PERCENTAGES[3])})"))
                print(summary)

                with open(f"results/performance_evaluation/dmp_bench/{dmp_name}/dmp_bench_{crypto_bench_name}_{work_bench_name}.txt", 'r+') as logfile:
                    content = logfile.read()
                    logfile.seek(0, 0)
                    logfile.write(summary + "\nResults:\n" + content)

if __name__ == "__main__":
    main()
