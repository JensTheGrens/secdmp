#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('tableau-colorblind10')

RESULTS_FOLDER = "results"
# RESULTS_FOLDER = "expected_results"

markers = ['o', 's', 'v', '^', 'd', 'p']
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

STYLES = {
    "permanent_disabling": 0,
    "selective_disabling": 1,
    "partitioning": 2,
    "secdmp": 3,
    "prospect": 4,
    "prospect_secdmp": 5
}

# 1. performance: Embench full

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
    "secdmp": "SecDMP",
    "prospect": "ProSpeCT",
    "prospect_secdmp": "ProSpeCT+SecDMP"
}

EMBENCH_BENCHMARK_NAMES = ("aha-mont64", "crc32", "depthconv", "edn", "huffbench",
                           "matmult-int", "md5sum", "nettle-aes", "nettle-sha256", "nsichneu",
                           "picojpeg", "qrduino", "sglib-combined", "slre", "statemate",
                           "tarfind", "ud", "wikisort", "xgboost", "geometric mean")

absolute_results_embench = {}
relative_results_embench = {}

def parse_embench_log(path):
    parsed_results = {}
    with open(path) as log:
        for line in log:
            columns = line.split()
            if len(columns) < 2:
                continue
            name, cycles = " ".join(columns[:-1]).lower(), columns[-1].replace(",", "")
            if cycles.isdigit() and name in EMBENCH_BENCHMARK_NAMES:
                parsed_results[name] = int(cycles)

    # assertions to check parsing is correct:
    assert(len(parsed_results) == len(EMBENCH_BENCHMARK_NAMES))
    for benchmark_name in EMBENCH_BENCHMARK_NAMES:
        assert(parsed_results[benchmark_name] > 0)
    return parsed_results


# extract absolute results from the .txt files
for (dmp_key, dmp_name) in DMPS.items():
    EMBENCH_RESULTS_FOLDER = f"{RESULTS_FOLDER}/performance_evaluation/embench/{dmp_key}"

    absolute_results_embench[dmp_key] = {}
    for sim in SIMS.keys():
        parsed_results = parse_embench_log(f"{EMBENCH_RESULTS_FOLDER}/{sim}.txt")
        absolute_results_embench[dmp_key][sim] = [parsed_results[benchmark] for benchmark in EMBENCH_BENCHMARK_NAMES]

# calculate the relative results from the absolute results:
for dmp_key in DMPS.keys():
    relative_results_embench[dmp_key] = {sim: [0] * len(EMBENCH_BENCHMARK_NAMES) for sim in SIMS.keys() if sim != "proteus_dmp"}
    for sim in relative_results_embench[dmp_key].keys():
        for i in range(len(EMBENCH_BENCHMARK_NAMES)):
            relative_results_embench[dmp_key][sim][i] = round(100*(absolute_results_embench[dmp_key][sim][i]-absolute_results_embench[dmp_key]["proteus_dmp"][i])/absolute_results_embench[dmp_key]["proteus_dmp"][i],1)

# plot figure

bar_width = 0.12
n = 5
offsets = (np.arange(n) - (n - 1) / 2) * bar_width
x = np.arange(5)

fig = plt.figure(figsize=(13, 16.2), constrained_layout=True)
subfigs = fig.subfigures(2, 2, hspace=0.02).flatten()

for k, ((dmp_key, dmp_name), subfig) in enumerate(zip(DMPS.items(), subfigs)):
    axes = subfig.subplots(4, 1, sharex=False, sharey=True)
    axes[0].set_title(f"{dmp_name}")

    for i, ax in enumerate(axes):
        for ((sim, res), dx) in zip(relative_results_embench[dmp_key].items(), offsets):
            dot, = ax.plot(x + dx, res[i*5:i*5+5], markers[STYLES[sim]], color=colors[STYLES[sim]], label=SIMS[sim])
            ax.vlines(x + dx, 0, res[i*5:i*5+5], linewidth=1.4, color=dot.get_color())

        ax.set_xticks(x, EMBENCH_BENCHMARK_NAMES[i*5:i*5+5])
        ax.set_ylabel('Overhead (%)')
        ax.set_ylim(-8, 8.5)
        ax.yaxis.set_major_locator(plt.MultipleLocator(3))
        ax.set_axisbelow(True)
        ax.yaxis.grid(True, linestyle='-', linewidth=0.5, color='black', alpha=0.4)
        ax.axhline(0, color='black', linewidth=0.4, zorder=1)

handles, labels = subfigs[0].axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', ncols=5)

fig.get_layout_engine().set(rect=(0, 0, 1, 0.973), wspace=0.05)

plt.savefig(f"{RESULTS_FOLDER}/work_embench.pdf", format="pdf", bbox_inches='tight', pad_inches=0.05)

# 2. performance: CoreMark, Array of pointers, SpMV

def parse_bench_file(path):
    parsed_results = {}
    with open(path) as log:
        for line in log:
            columns = line.split()
            if len(columns) != 3:
                continue
            sim = columns[0].replace(":", "")
            cycles = columns[1]
            assert(columns[2] == "cycles")
            parsed_results[sim] = int(cycles)

    # assertions to check parsing is correct:
    assert(len(parsed_results) == len(SIMS))
    for sim in SIMS.keys():
        assert(parsed_results[sim] > 0)
    return parsed_results

BENCHMARKS = {
    "coremark": "CoreMark",
    "array_of_pointers": "AoP",
    "spmv": "SpMV"
}

absolute_results = {}
relative_results = {}

# extract absolute results from the .txt files
for (dmp_key, dmp_name) in DMPS.items():
    absolute_results[dmp_key] = {sim: [] for sim in SIMS.keys()}
    for (bench_key, bench_name) in BENCHMARKS.items():
        BENCH_RESULTS_FILE = f"{RESULTS_FOLDER}/performance_evaluation/{bench_key}/{dmp_key}/{bench_key}.txt"
        parsed_results = parse_bench_file(BENCH_RESULTS_FILE)
        for sim in SIMS.keys():
            absolute_results[dmp_key][sim].append(parsed_results[sim])

# calculate relative results
for dmp_key in DMPS.keys():
    relative_results[dmp_key] = {sim: [0] * len(BENCHMARKS) for sim in SIMS.keys() if sim != "proteus_dmp"}
    for sim in relative_results[dmp_key].keys():
        for i in range(len(BENCHMARKS)):
            relative_results[dmp_key][sim][i] = round(100*(absolute_results[dmp_key][sim][i]-absolute_results[dmp_key]["proteus_dmp"][i])/absolute_results[dmp_key]["proteus_dmp"][i],1)

# plot figure

bar_width = 0.12
n = len(SIMS) - 1
offsets = (np.arange(n) - (n - 1) / 2) * bar_width
x = np.arange(len(BENCHMARKS))

fig, axes = plt.subplots(1, len(DMPS), figsize=(13, 2.4), sharex=True, sharey=True)
axes = axes.flatten()

ymax = max(value for dmp_results in relative_results.values() for res in dmp_results.values() for value in res)

for i, ((dmp_key, dmp_name), ax) in enumerate(zip(DMPS.items(), axes)):
    for ((sim, res), dx) in zip(relative_results[dmp_key].items(), offsets):
        dot, = ax.plot(x + dx, res, markers[STYLES[sim]], color=colors[STYLES[sim]], label=SIMS[sim])
        ax.vlines(x + dx, 0, res, linewidth=1.4, color=dot.get_color())

    ax.set_xticks(x, list(BENCHMARKS.values()))
    ax.yaxis.grid(True, linestyle='-', linewidth=0.5, color='black', alpha=0.4)
    ax.set_axisbelow(True)
    ax.set_title(dmp_name)
    ax.set_xlim(-0.5, len(BENCHMARKS) - 0.5)
    ax.set_ylim(-0.1*ymax, 1.15*ymax)
    ax.axhline(0, color='black', linewidth=0.4, zorder=1)
    if i == 0:
        ax.set_ylabel("Overhead (%)")
    else:
        ax.set_ylabel("")
        ax.tick_params(axis='y', labelleft=False)

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', ncols=5)

plt.tight_layout(rect=[0, 0, 1, 0.90])

plt.savefig(f"{RESULTS_FOLDER}/work_coremark_aop_spmv.pdf", format="pdf", bbox_inches='tight', pad_inches=0.05)

# 3. sglib coremark aop spmv

BENCHMARKS = {
    "coremark": "CoreMark",
    "array_of_pointers": "AoP",
    "spmv": "SpMV"
}

# sglib-combined comes from the embench results, the other benchmarks from section 2
SGLIB_INDEX = EMBENCH_BENCHMARK_NAMES.index("sglib-combined")
MAIN_BENCHMARK_NAMES = ["Sglib"] + list(BENCHMARKS.values())

relative_results_main = {}
for dmp_key in DMPS.keys():
    relative_results_main[dmp_key] = {sim: [relative_results_embench[dmp_key][sim][SGLIB_INDEX]] + relative_results[dmp_key][sim]
                                      for sim in SIMS.keys() if sim != "proteus_dmp"}

# plot figure

bar_width = 0.16
n = len(SIMS) - 1
offsets = (np.arange(n) - (n - 1) / 2) * bar_width
x = np.arange(len(MAIN_BENCHMARK_NAMES))

fig, axes = plt.subplots(1, len(DMPS), figsize=(13, 2.4), sharex=True, sharey=True)
axes = axes.flatten()

ymax = max(value for dmp_results in relative_results_main.values() for res in dmp_results.values() for value in res)

for i, ((dmp_key, dmp_name), ax) in enumerate(zip(DMPS.items(), axes)):
    for ((sim, res), dx) in zip(relative_results_main[dmp_key].items(), offsets):
        dot, = ax.plot(x + dx, res, markers[STYLES[sim]], color=colors[STYLES[sim]], label=SIMS[sim])
        ax.vlines(x + dx, 0, res, linewidth=1.4, color=dot.get_color())

    ax.set_xticks(x, MAIN_BENCHMARK_NAMES)
    ax.yaxis.grid(True, linestyle='-', linewidth=0.5, color='black', alpha=0.4)
    ax.set_axisbelow(True)
    ax.set_title(dmp_name)
    ax.set_xlim(-0.5, len(MAIN_BENCHMARK_NAMES) - 0.5)
    ax.set_ylim(-0.1*ymax, 1.15*ymax)
    ax.axhline(0, color='black', linewidth=0.4, zorder=1)
    if i == 0:
        ax.set_ylabel("Overhead (%)")
    else:
        ax.set_ylabel("")
        ax.tick_params(axis='y', labelleft=False)

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', ncols=5)

plt.tight_layout(rect=[0, 0, 1, 0.90])

plt.savefig(f"{RESULTS_FOLDER}/work_figure.pdf", format="pdf", bbox_inches='tight', pad_inches=0.05)

# 4. overhead of permanent disabling

BENCHMARKS = {
    "coremark": "CoreMark",
    "array_of_pointers": "AoP",
    "spmv": "SpMV"
}
MAIN_BENCHMARK_NAMES = ["Sglib"] + list(BENCHMARKS.values())

# plot figure

bar_width = 0.12
n = len(DMPS)
offsets = (np.arange(n) - (n - 1) / 2) * bar_width
x = np.arange(len(MAIN_BENCHMARK_NAMES))

fig, ax = plt.subplots(figsize=(6.4, 2.4))

ymax = max(value for res in relative_results_main.values() for value in res["permanent_disabling"])

for j, ((dmp_key, dmp_name), dx) in enumerate(zip(DMPS.items(), offsets)):
    res = relative_results_main[dmp_key]["permanent_disabling"]
    dot, = ax.plot(x + dx, res, markers[j], label=dmp_name)
    ax.vlines(x + dx, 0, res, linewidth=1.4, color=dot.get_color())

ax.set_xticks(x, MAIN_BENCHMARK_NAMES)
ax.yaxis.grid(True, linestyle='-', linewidth=0.5, color='black', alpha=0.4)
ax.set_axisbelow(True)
ax.set_ylabel("Overhead (%)")
ax.set_xlim(-0.5, len(MAIN_BENCHMARK_NAMES) - 0.5)
ax.set_ylim(-0.1*ymax, 1.15*ymax)
ax.axhline(0, color='black', linewidth=0.4, zorder=1)

handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', ncols=4)

plt.tight_layout(rect=[0, 0, 1, 0.87])

plt.savefig(f"{RESULTS_FOLDER}/work_dmp_disabling_overhead.pdf", format="pdf", bbox_inches='tight', pad_inches=0.05)

print(f"Figures saved in folder: {RESULTS_FOLDER}")
