#!/usr/bin/env python3

import subprocess
import os
from waveform_analysis.signal_extractor import CPUWaveform
from waveform_analysis.interface_parser import proteus_o_parser

SIM_BUILD_FOLDER = "ecosystem/simulation/build/sim"
DMP_PROGRAMS_FOLDER = "benchmarks/security/dmp_tests"
DMP_ATTACKS = ["imp_leak", "augury_poc", "gofetch_poc", "peek_a_walk", "dmp_spectre", "recursion"]
DMP_LEAKAGE_TESTS = ["load_secret", "same_cache_block", "transient_load"]
SPECTRE_PROGRAMS_FOLDER = "benchmarks/security/spectre_tests/build"
SPECTRE_TESTS = ["pht_load", "pht_store", "pht_branch", "pht_jump", "pht_division"]
DMPS = ["AppleDmp", "IntelDmp", "Cdp", "Imp"]
RESULTS_FOLDER = "results/security_evaluation"
RESULTS_FILE = "security_evaluation_results.txt"

def init_log_file(folder, file):
    os.makedirs(folder, exist_ok=True)
    open(f"{folder}/{file}", 'w').close()

def print_and_log(path, text = ""):
    print(text)
    with open(path, 'a') as logfile:
        logfile.write(text + "\n")

def center(text, width):
    padding = max(width - sum(2 if char in "✅❌" else 1 for char in text), 0)
    return " " * (padding // 2) + text + " " * (padding - padding // 2)

def row(name, cells):
    return "{:<35}".format(name) + "".join(center(cell, 10) for cell in cells)

def run_and_parse(dmp, sim, program, variant):
    subprocess.run([f"{SIM_BUILD_FOLDER}/{dmp}/{sim}", "--dump-fst", f"sim{variant}.fst", program], stdout=subprocess.DEVNULL, check=True)
    return CPUWaveform(f"sim{variant}.fst", proteus_o_parser)

# returns true if all checked signals are equal
def noninterference_check(waveform1, waveform2, include_dmp_signal):
    policy_signals = waveform1.liberal_security_filter()
    if include_dmp_signal:
        policy_signals.append("TOP.Core.pipeline.dataPrefetcher_noninterferenceSignals")
    return waveform1.compare_signals(waveform2, policy_signals, timing_sensitive = True)

def run_and_check_noninterference(path, sim, programs, folder, variant_1, variant_2, has_dmp):
    for (program, include_dmp_signal) in programs:
        program1 = f"{folder}/{program}_{variant_1}.bin"
        program2 = f"{folder}/{program}_{variant_2}.bin"

        results = []
        for dmp in DMPS:
            waveform_1 = run_and_parse(dmp, sim, program1, variant_1)
            waveform_2 = run_and_parse(dmp, sim, program2, variant_2)

            secure = noninterference_check(waveform_1, waveform_2, has_dmp and include_dmp_signal)
            results.append("✅" if secure else "❌")

        print_and_log(path, row(program, results))

def run_security_eval(path, sim, programs, folder, variant_1, variant_2, has_dmp):
    print_and_log(path, f"Results for {sim}:")
    run_and_check_noninterference(path, sim, programs, folder, variant_1, variant_2, has_dmp)
    print_and_log(path)

def print_table_header(path, title):
    print_and_log(path, title)
    print_and_log(path, row("", [center("Secure", 40)]))
    print_and_log(path, row("", DMPS))

if __name__ == "__main__":
    init_log_file(RESULTS_FOLDER, RESULTS_FILE)
    path = f"{RESULTS_FOLDER}/{RESULTS_FILE}"

    dmp_programs = [(program, False) for program in DMP_ATTACKS] + [(program, True) for program in DMP_LEAKAGE_TESTS]

    print_table_header(path, "Part 1: DMP security tests:")
    run_security_eval(path, "proteus_dmp", dmp_programs, f"{DMP_PROGRAMS_FOLDER}/default", "0", "1", has_dmp=True)
    run_security_eval(path, "permanent_disabling", dmp_programs, f"{DMP_PROGRAMS_FOLDER}/default", "0", "1", has_dmp=False)
    run_security_eval(path, "selective_disabling", dmp_programs, f"{DMP_PROGRAMS_FOLDER}/security_modes", "0", "1", has_dmp=True)
    run_security_eval(path, "secdmp", dmp_programs, f"{DMP_PROGRAMS_FOLDER}/secret_partitioning", "0", "1", has_dmp=True)
    run_security_eval(path, "prospect", dmp_programs, f"{DMP_PROGRAMS_FOLDER}/secret_partitioning", "0", "1", has_dmp=True)
    run_security_eval(path, "prospect_secdmp", dmp_programs, f"{DMP_PROGRAMS_FOLDER}/secret_partitioning", "0", "1", has_dmp=True)
    print_and_log(path)

    spectre_programs = [(program, True) for program in SPECTRE_TESTS]

    print_table_header(path, "Part 2: Spectre security tests:")
    run_security_eval(path, "proteus_dmp", spectre_programs, f"{SPECTRE_PROGRAMS_FOLDER}/default", "0", "1", has_dmp=True)
    run_security_eval(path, "permanent_disabling", spectre_programs, f"{SPECTRE_PROGRAMS_FOLDER}/default", "0", "1", has_dmp=False)
    run_security_eval(path, "selective_disabling", spectre_programs, f"{SPECTRE_PROGRAMS_FOLDER}/security_modes", "0", "1", has_dmp=True)
    run_security_eval(path, "secdmp", spectre_programs, f"{SPECTRE_PROGRAMS_FOLDER}/secret_partitioning", "0", "1", has_dmp=True)
    run_security_eval(path, "prospect", spectre_programs, f"{SPECTRE_PROGRAMS_FOLDER}/secret_partitioning", "0", "1", has_dmp=True)
    run_security_eval(path, "prospect_secdmp", spectre_programs, f"{SPECTRE_PROGRAMS_FOLDER}/secret_partitioning", "0", "1", has_dmp=True)
