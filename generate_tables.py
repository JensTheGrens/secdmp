#!/usr/bin/env python3

RESULTS_FOLDER = "results"
# RESULTS_FOLDER = "expected_results"
CRYPTO_RESULTS_FOLDER = f"{RESULTS_FOLDER}/performance_evaluation/hacl_crypto"

DMPS = {
    "AppleDmp": "Apple DMP",
    "IntelDmp": "Intel DMP",
    "Cdp": "CDP",
    "Imp": "IMP"
}

SIMS = {
    "permanent_disabling": "Permanent Disabling",
    "selective_disabling": "Selective Disabling",
    "partitioning": "Partitioning",
    "secdmp": r"\secdmp{}",
    "prospect": r"\prospect{}",
    "prospect_secdmp": r"\prospect{}+\secdmp{}"
}

CRYPTO = {
    "chacha20": "Chacha20",
    "salsa20": "Salsa20",
    "sha2": "SHA2",
    "hmac": "HMAC",
    "hkdf": "HKDF"
}

ALL_SIMS = ["proteus_dmp"] + list(SIMS.keys())

absolute_results_crypto = {}


def parse_crypto_log(path):
    parsed_results = {}
    with open(path) as log:
        for line in log:
            columns = line.split()
            if len(columns) < 2:
                continue
            sim, cycles = columns[0], columns[1]
            if sim in ALL_SIMS and cycles.isdigit():
                parsed_results[sim] = int(cycles)

    # assertions to check parsing is correct:
    assert(len(parsed_results) == len(ALL_SIMS))
    for sim in ALL_SIMS:
        assert(parsed_results[sim] > 0)
    return parsed_results


# extract absolute results from the .txt files
for dmp_key in DMPS.keys():
    for benchmark in CRYPTO.keys():
        absolute_results_crypto[(dmp_key, benchmark)] = parse_crypto_log(
            f"{CRYPTO_RESULTS_FOLDER}/{dmp_key}/{benchmark}.txt")


def relative_result(dmp_key, benchmark, sim):
    results = absolute_results_crypto[(dmp_key, benchmark)]
    overhead = 100 * (results[sim] - results["proteus_dmp"]) / results["proteus_dmp"]
    overhead = round(overhead, 1)
    return f"\\num{{{'-' if overhead < 0 else '+'}{abs(overhead):.1f}}}"

# hacl* results table
DMPS_PER_BLOCK = 2
dmp_keys = list(DMPS.keys())
DMP_BLOCKS = [dmp_keys[i:i + DMPS_PER_BLOCK] for i in range(0, len(dmp_keys), DMPS_PER_BLOCK)]

lines = [
    r"\begin{table*}[t]",
    r"  \centering",
    r"  \caption{Performance overhead in \% on the HACL* primitives per DMP, relative to Proteus+DMP.}",
    r"  \label{tab:hacl-results}",
    r"  \begin{tabular}{l" + " c" * (len(CRYPTO) * DMPS_PER_BLOCK) + r"}\toprule",
]
for block_index, dmp_block in enumerate(DMP_BLOCKS):
    if block_index > 0:
        lines.append(r"    \midrule")
    lines += [
        r"    \multirow{2}{*}{Defense}"
        + "".join(f" & \\multicolumn{{{len(CRYPTO)}}}{{c}}{{{DMPS[dmp_key]}}}" for dmp_key in dmp_block)
        + r" \\",
        "  " + "".join(f"\\cmidrule(lr){{{2 + len(CRYPTO)*i}-{1 + len(CRYPTO)*(i + 1)}}}"
                       for i in range(len(dmp_block))),
        "    " + "".join(f" & {name}" for _ in dmp_block for name in CRYPTO.values())
        + r" \\ \midrule",
    ]
    for (sim, sim_name) in SIMS.items():
        row = f"    {sim_name}"
        for dmp_key in dmp_block:
            for benchmark in CRYPTO.keys():
                row += " & " + relative_result(dmp_key, benchmark, sim)
        lines.append(row + r" \\")
lines += [r"    \bottomrule", r"  \end{tabular}", r"\end{table*}"]

with open(f"{RESULTS_FOLDER}/hacl_table.tex", "w") as logfile:
    logfile.write("\n".join(lines) + "\n")

WORK = {
    "sglib-combined": "Sglib",
    "coremark": "CoreMark",
    "array_of_pointers": "AoP",
    "spmv": "SpMV"
}

WORK_PERCENTAGES = ("25", "50", "75", "90")

DMPS_WITH_ARTICLE = ("AppleDmp", "IntelDmp")

DMP_BENCH_RESULTS_FOLDER = f"{RESULTS_FOLDER}/performance_evaluation/dmp_bench"

absolute_results_dmp_bench = {}

def parse_dmp_bench_log(path):
    parsed_results = {}
    with open(path) as log:
        for line in log:
            columns = line.split()
            if len(columns) < 2:
                continue
            sim, cycles = columns[0], [int(c) for c in columns[1:] if c.isdigit()]
            if sim in ALL_SIMS and len(cycles) == len(WORK_PERCENTAGES):
                parsed_results[sim] = cycles

    # assertions to check parsing is correct:
    assert(len(parsed_results) == len(ALL_SIMS))
    for sim in ALL_SIMS:
        assert(all(cycles > 0 for cycles in parsed_results[sim]))
    return parsed_results


# extract absolute results from the .txt files
for dmp_key in DMPS.keys():
    for benchmark in CRYPTO.keys():
        for work in WORK.keys():
            absolute_results_dmp_bench[(dmp_key, benchmark, work)] = parse_dmp_bench_log(
                f"{DMP_BENCH_RESULTS_FOLDER}/{dmp_key}/dmp_bench_{benchmark}_{work}.txt")


def relative_result_dmp_bench(dmp_key, benchmark, work, sim, percentage_index):
    results = absolute_results_dmp_bench[(dmp_key, benchmark, work)]
    proteus_dmp = results["proteus_dmp"][percentage_index]
    overhead = 100 * (results[sim][percentage_index] - proteus_dmp) / proteus_dmp
    overhead = round(overhead, 1)
    return f"{'-' if overhead < 0 else '+'}{abs(overhead):.1f}"


# dmp-bench results tables, one per dmp
lines = []
for (dmp_key, dmp_name) in DMPS.items():
    article = "the " if dmp_key in DMPS_WITH_ARTICLE else ""
    lines += [
        r"\begin{table*}[t]",
        r"  \centering",
        f"  \\caption{{Performance overhead in \\% on DMP-Bench for {article}{dmp_name}, relative to "
        r"Proteus+DMP.}",
        f"  \\label{{tab:dmp-bench-{dmp_key}}}",
        r"  \setlength{\tabcolsep}{1.9pt}",
        r"  \begin{tabular}{l" + " S[table-format=+2.1]" * (len(WORK_PERCENTAGES) * len(WORK)) + r"}\toprule",
        r"    \multirow{2}{*}{Defense}"
        + "".join(f" & \\multicolumn{{{len(WORK_PERCENTAGES)}}}{{c}}{{{name}}}" for name in WORK.values())
        + r" \\",
        "  " + "".join(f"\\cmidrule(lr){{{2 + len(WORK_PERCENTAGES)*i}-{1 + len(WORK_PERCENTAGES)*(i + 1)}}}"
                       for i in range(len(WORK))),
        "    " + "".join(f" & \\multicolumn{{1}}{{c}}{{{percentage}\\%\\,W}}"
                         for _ in WORK.keys() for percentage in WORK_PERCENTAGES)
        + r" \\ \midrule",
    ]
    for (benchmark_index, (benchmark, benchmark_name)) in enumerate(CRYPTO.items()):
        if benchmark_index > 0:
            lines.append(r"    \midrule")
        lines.append(f"    \\multicolumn{{{1 + len(WORK_PERCENTAGES)*len(WORK)}}}{{l}}"
                     f"{{\\emph{{{benchmark_name}}}}} \\\\")
        for (sim, sim_name) in SIMS.items():
            row = f"    {sim_name}"
            for work in WORK.keys():
                for percentage_index in range(len(WORK_PERCENTAGES)):
                    row += " & " + relative_result_dmp_bench(dmp_key, benchmark, work, sim, percentage_index)
            lines.append(row + r" \\")
    lines += [r"    \bottomrule", r"  \end{tabular}", r"\end{table*}", ""]

with open(f"{RESULTS_FOLDER}/dmp_bench_table.tex", "w") as logfile:
    logfile.write("\n".join(lines) + "\n")

HARDWARE_RESULTS_FOLDER = f"{RESULTS_FOLDER}/hardware_evaluation"

HARDWARE_SIMS = {
    "proteus_dmp": "Proteus+DMP",
    "selective_disabling": "Selective Disabling",
    "secdmp": r"\secdmp{}",
    "prospect": r"\prospect{}",
    "prospect_secdmp": r"\prospect{}+\secdmp{}"
}


def parse_hardware_log(path):
    area, parsed_result = None, None
    with open(path) as log:
        for line in log:
            columns = line.split()
            if columns[:2] == ["Area", "="]:
                area = columns[-2]
            elif columns[:2] == ["Timing", "met:"]:
                parsed_result = (columns[columns.index("ns") - 1], area)

    # assertions to check parsing is correct:
    assert(parsed_result is not None)
    assert(all(value is not None for value in parsed_result))
    return parsed_result


# extract the results from the .txt files
results_hardware = {("proteus", dmp_key): parse_hardware_log(f"{HARDWARE_RESULTS_FOLDER}/permanent_disabling.txt")
                    for dmp_key in DMPS.keys()}
for dmp_key in DMPS.keys():
    for sim in HARDWARE_SIMS.keys():
        results_hardware[(sim, dmp_key)] = parse_hardware_log(
            f"{HARDWARE_RESULTS_FOLDER}/{dmp_key}/{sim}.txt")


# hardware evaluation table
lines = [
    r"\begin{table}[t]",
    r"  \centering",
    r"  \caption{Results of the hardware evaluation.}",
    r"  \label{tab:hardware-evaluation}",
    r"  \begin{tabular}{l" + " c" * len(DMPS) + r"}\toprule",
    r"    \multirow{2}{*}{Defense} & \multicolumn{" + str(len(DMPS))
    + r"}{c}{Area (\si{\milli\meter\squared})} \\",
    f"  \\cmidrule(lr){{2-{1 + len(DMPS)}}}",
    "    " + "".join(f" & {name}" for name in DMPS.values()) + r" \\ \midrule",
]
for (sim, sim_name) in {"proteus": "Proteus", **HARDWARE_SIMS}.items():
    row = f"    {sim_name}"
    for dmp_key in DMPS.keys():
        row += " & " + results_hardware[(sim, dmp_key)][1]
    lines.append(row + r" \\")
lines += [r"    \bottomrule", r"  \end{tabular}", r"\end{table}"]

with open(f"{RESULTS_FOLDER}/hardware_table.tex", "w") as logfile:
    logfile.write("\n".join(lines) + "\n")

print(f"Tables saved in folder: {RESULTS_FOLDER}")
