#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('tableau-colorblind10')

RESULTS_FOLDER = "results"
# RESULTS_FOLDER = "expected_results"

markers = ['o', 's', 'v', '^', 'd', 'p']
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

# performance: hacl* crypto

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

CRYPTO_BENCHMARK_NAMES = tuple(CRYPTO.keys())

STYLES = {
    "permanent_disabling": 0,
    "selective_disabling": 1,
    "partitioning": 2,
    "secdmp": 3,
    "prospect": 4,
    "prospect_secdmp": 5
}

absolute_results_crypto = {}
relative_results_crypto = {}

def parse_crypto_log(path):
    parsed_results = {}
    with open(path) as log:
        for line in log:
            columns = line.split()
            if len(columns) < 2:
                continue
            sim, cycles = columns[0], columns[1]
            if sim in SIMS and cycles.isdigit():
                parsed_results[sim] = int(cycles)

    # assertions to check parsing is correct:
    assert(len(parsed_results) == len(SIMS))
    for sim in SIMS.keys():
        assert(parsed_results[sim] > 0)
    return parsed_results


# extract absolute results from the .txt files
for (dmp_key, dmp_name) in DMPS.items():
    CRYPTO_RESULTS_FOLDER = f"{RESULTS_FOLDER}/performance_evaluation/hacl_crypto/{dmp_key}"

    absolute_results_crypto[dmp_key] = {}
    for sim in SIMS.keys():
        absolute_results_crypto[dmp_key][sim] = [parse_crypto_log(f"{CRYPTO_RESULTS_FOLDER}/{benchmark}.txt")[sim]
                                                 for benchmark in CRYPTO_BENCHMARK_NAMES]

# calculate the relative results from the absolute results:
for dmp_key in DMPS.keys():
    relative_results_crypto[dmp_key] = {sim: [0] * len(CRYPTO_BENCHMARK_NAMES) for sim in SIMS.keys() if sim != "proteus_dmp"}
    for sim in relative_results_crypto[dmp_key].keys():
        for i in range(len(CRYPTO_BENCHMARK_NAMES)):
            relative_results_crypto[dmp_key][sim][i] = round(100*(absolute_results_crypto[dmp_key][sim][i]-absolute_results_crypto[dmp_key]["proteus_dmp"][i])/absolute_results_crypto[dmp_key]["proteus_dmp"][i],1)


bar_width = 0.12
n = len(SIMS) - 1
offsets = (np.arange(n) - (n - 1) / 2) * bar_width

# plot figure

ymin = min(value for dmp_results in relative_results_crypto.values()
           for res in dmp_results.values() for value in res)
ymax = max(value for dmp_results in relative_results_crypto.values()
           for res in dmp_results.values() for value in res)

fig, axes = plt.subplots(len(DMPS), 1, figsize=(5.7, 6.8), sharex=True, sharey=True)
axes = axes.flatten()
x = np.arange(len(CRYPTO))

for ((dmp_key, dmp_name), ax) in zip(DMPS.items(), axes):
    for ((sim, res), dx) in zip(relative_results_crypto[dmp_key].items(), offsets):
        dot, = ax.plot(x + dx, res, markers[STYLES[sim]], color=colors[STYLES[sim]], label=SIMS[sim])
        ax.vlines(x + dx, 0, res, linewidth=1.4, color=dot.get_color())

    ax.set_xticks(x, list(CRYPTO.values()))
    ax.tick_params(axis='x', labelbottom=True)
    ax.set_title(dmp_name)
    ax.set_xlim(-0.5, len(CRYPTO) - 0.5)
    ax.set_ylim(min(1.4*ymin, -0.1*ymax), 1.2*ymax)
    ax.yaxis.set_major_locator(plt.MultipleLocator(2))
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle='-', linewidth=0.5, color='black', alpha=0.4)
    ax.axhline(0, color='black', linewidth=0.4, zorder=1)
    ax.set_ylabel("Overhead (%)")

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', ncols=3, frameon=True, framealpha=1.0)
plt.tight_layout(rect=[0, 0, 1, 0.93])

plt.savefig(f"{RESULTS_FOLDER}/hacl_crypto.pdf", format="pdf", bbox_inches='tight', pad_inches=0.05)

print(f"Figures saved in folder: {RESULTS_FOLDER}")
