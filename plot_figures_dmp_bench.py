#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('tableau-colorblind10')

RESULTS_FOLDER = "results"
# RESULTS_FOLDER = "expected_results"

markers = ['o', 's', 'v', '^', 'd', 'p']
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

# performance: dmp bench

DMPS = {
    "AppleDmp": "Apple DMP",
    "IntelDmp": "Intel DMP",
    "Cdp": "CDP",
    "Imp": "IMP"
}

SIMS = {
    "proteus_dmp": "Proteus+DMP",
    "permanent_disabling": "Permanent Disabling",
    "selective_disabling": "Selective Disabling",
    "partitioning": "Partitioning",
    "secdmp": "SecDMP",
    "prospect": "ProSpeCT",
    "prospect_secdmp": "ProSpeCT+SecDMP"
}

CRYPTO = {
    "chacha20": "Chacha20",
    "salsa20": "Salsa20",
    "sha2": "SHA2",
    "hmac": "HMAC",
    "hkdf": "HKDF"
}

WORK_FUNCTIONS = {
    "sglib-combined": "Sglib",
    "coremark": "CoreMark",
    "array_of_pointers": "AoP",
    "spmv": "SpMV"
}

COMBINATIONS = [(crypto_key, work_key) for crypto_key in CRYPTO.keys() for work_key in WORK_FUNCTIONS.keys()]

WORK_PERCENTAGES = (25, 50, 75, 90)

STYLES = {
    "permanent_disabling": 0,
    "selective_disabling": 1,
    "partitioning": 2,
    "secdmp": 3,
    "prospect": 4,
    "prospect_secdmp": 5
}

LINESTYLES = {
    "permanent_disabling": "-",
    "selective_disabling": "--",
    "partitioning": "-.",
    "secdmp": ":",
    "prospect": (0, (7, 3)),
    "prospect_secdmp": (0, (3, 4, 1, 4, 1, 4))
}

absolute_results_dmp_bench = {}
relative_results_dmp_bench = {}
geomean_results_dmp_bench = {}

def parse_dmp_bench_log(path):
    parsed_results = {}
    with open(path) as log:
        for line in log:
            columns = line.split()
            if len(columns) < 2 or columns[0] not in SIMS:
                continue
            parsed_results[columns[0]] = [int(cycles) for cycles in columns[1:] if cycles.isdigit()]

    # assertions to check parsing is correct:
    assert(len(parsed_results) == len(SIMS))
    for sim in SIMS.keys():
        assert(len(parsed_results[sim]) == len(WORK_PERCENTAGES))
        for cycles in parsed_results[sim]:
            assert(cycles > 0)
    return parsed_results


# extract absolute results from the .txt files
for (dmp_key, dmp_name) in DMPS.items():
    DMP_BENCH_RESULTS_FOLDER = f"{RESULTS_FOLDER}/performance_evaluation/dmp_bench/{dmp_key}"

    absolute_results_dmp_bench[dmp_key] = {sim: [] for sim in SIMS.keys()}
    for (crypto_key, work_key) in COMBINATIONS:
        parsed_results = parse_dmp_bench_log(f"{DMP_BENCH_RESULTS_FOLDER}/dmp_bench_{crypto_key}_{work_key}.txt")
        for sim in SIMS.keys():
            absolute_results_dmp_bench[dmp_key][sim].append(parsed_results[sim])

# calculate the relative results from the absolute results:
for dmp_key in DMPS.keys():
    relative_results_dmp_bench[dmp_key] = {sim: [] for sim in SIMS.keys() if sim != "proteus_dmp"}
    for sim in relative_results_dmp_bench[dmp_key].keys():
        for c in range(len(COMBINATIONS)):
            proteus_dmp = absolute_results_dmp_bench[dmp_key]["proteus_dmp"][c]
            cycles = absolute_results_dmp_bench[dmp_key][sim][c]
            relative_results_dmp_bench[dmp_key][sim].append([round(100*(cycles[i]-proteus_dmp[i])/proteus_dmp[i],1)
                                                             for i in range(len(WORK_PERCENTAGES))])

# calculate geometric mean over every work function x cryptographic primitive, per dmp:
for dmp_key in DMPS.keys():
    geomean_results_dmp_bench[dmp_key] = {sim: [0] * len(WORK_PERCENTAGES) for sim in SIMS.keys() if sim != "proteus_dmp"}
    for sim in geomean_results_dmp_bench[dmp_key].keys():
        for i in range(len(WORK_PERCENTAGES)):
            ratios = [absolute_results_dmp_bench[dmp_key][sim][c][i]/absolute_results_dmp_bench[dmp_key]["proteus_dmp"][c][i]
                      for c in range(len(COMBINATIONS))]
            geomean_results_dmp_bench[dmp_key][sim][i] = round(100*(np.prod(ratios)**(1/len(ratios))-1),3)

# plot figure

fig, axes = plt.subplots(1, len(DMPS), figsize=(13, 2.5), sharex=True, sharey=True)
axes = axes.flatten()

ymin = min(value for dmp_results in geomean_results_dmp_bench.values()
           for res in dmp_results.values() for value in res)
ymax = max(value for dmp_results in geomean_results_dmp_bench.values()
           for res in dmp_results.values() for value in res)

for i, ((dmp_key, dmp_name), ax) in enumerate(zip(DMPS.items(), axes)):
    for (sim, res) in geomean_results_dmp_bench[dmp_key].items():
        ax.plot(WORK_PERCENTAGES, res, marker=markers[STYLES[sim]], color=colors[STYLES[sim]],
                linestyle=LINESTYLES[sim], label=SIMS[sim])

    ax.set_xticks(WORK_PERCENTAGES)
    ax.yaxis.grid(True, linestyle='-', linewidth=0.5, color='black', alpha=0.4)
    ax.set_axisbelow(True)
    ax.set_title(dmp_name)
    ax.set_ylim(1.15*ymin, 1.15*ymax)
    ax.axhline(0, color='black', linewidth=0.4, zorder=1)
    ax.set_xlabel("Work Function (%)")
    if i == 0:
        ax.set_ylabel("Overhead (%)")
    else:
        ax.set_ylabel("")
        ax.tick_params(axis='y', labelleft=False)

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', ncols=6, frameon=True, framealpha=1.0)

plt.tight_layout(rect=[0, 0, 1, 0.90])

plt.savefig(f"{RESULTS_FOLDER}/dmp_bench.pdf", format="pdf", bbox_inches='tight', pad_inches=0.05)

print(f"Figures saved in folder: {RESULTS_FOLDER}")
