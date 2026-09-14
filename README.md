# SecDMP: Provably Secure Data Memory-Dependent Prefetching
This is the repository for the SecDMP paper published at NDSS 2027, containing all artifacts of the implementation and evaluation

```bibtex
@inproceedings{sprengers27secdmp,
  title     = {SecDMP: Provably Secure Data Memory-Dependent Prefetching},
  author    = {Sprengers, Jens and Bognar, Marton and Daniel, Lesly-Ann and Piessens, Frank},
  year      = {2027},
  booktitle = {Network and Distributed System Security Symposium (NDSS)},
  doi       = {},
  pages     = {},
  url       = {},
}
```

## Table of Contents
- [Artifacts](#artifacts)
  - [Repository Structure](#repository-structure)
  - [DMP Implementations](#dmp-implementations)
  - [Defenses](#defenses)
- [Setup](#setup---20-minutes)
  - [Docker](#docker-recommended)
  - [Local Setup](#local-setup)
- [Minimal Working Example](#minimal-working-example---1-minute)
- [Running the evaluation](#running-the-evaluation)
  - [Running the Entire Evaluation](#running-the-entire-evaluation)
  - [Building the Processor Simulations](#building-the-processor-simulations---60-minutes)
  - [Compiling Benchmarks](#compiling-benchmarks---15-minutes)
  - [Security Evaluation](#security-evaluation---20-minutes)
  - [Performance Evaluation](#performance-evaluation)
  - [Hardware Evaluation](#hardware-evaluation---8-hours)
  - [Generating Figures and Tables](#generating-figures-and-tables)

# Artifacts
## Repository Structure
- [benchmarks](benchmarks) - contains the security and performance benchmarks
- [ecosystem](ecosystem) - a stripped version of the [Proteus ecosystem](https://github.com/proteus-core/ecosystem), keeping only what is necessary
- [expected_results](expected_results) - the expected output when running the evaluation
- [proteus](proteus) - the [RISC-V Proteus processor](https://github.com/proteus-core/proteus) extended with our DMPs and the defenses.
- The root folder contains scripts for running the evaluation (see below) and generating the figures and tables

## DMP Implementations
The open-source DMPs are located at:
- [PointerChasingDmp.scala](proteus/src/main/scala/riscv/plugins/memory/PointerChasingDmp.scala) for the Apple DMP and CDP,
- [ArrayOfPointersDmp.scala](proteus/src/main/scala/riscv/plugins/memory/ArrayOfPointersDmp.scala) for the Intel DMP,
- [IndirectArrayPatternDmp.scala](proteus/src/main/scala/riscv/plugins/memory/IndirectArrayPatternDmp.scala) for IMP.

They are instantiated with their parameters at [Config.scala](proteus/src/main/scala/riscv/Config.scala)

## Defenses
The configurations for the different Proteus processor cores for the different defenses are found at the bottom of [Core.scala](proteus/src/main/scala/riscv/Core.scala) (starting at line 468)

We created the plugins: [SecDmp.scala](proteus/src/main/scala/riscv/plugins/SecDmp.scala), [MemoryPartitioning.scala](proteus/src/main/scala/riscv/plugins/MemoryPartitioning.scala), [SelectivePrefetcherDisabling.scala](proteus/src/main/scala/riscv/plugins/SelectivePrefetcherDisabling.scala), [SecurityController.scala](proteus/src/main/scala/riscv/plugins/SecurityController.scala) and modified [Cache.scala](proteus/src/main/scala/riscv/plugins/Cache.scala).


- [SecDmp.scala](proteus/src/main/scala/riscv/plugins/SecDmp.scala) is the plugin of the SecDMP defense, which uses:
- [MemoryPartitioning.scala](proteus/src/main/scala/riscv/plugins/MemoryPartitioning.scala) to partition memory using CSRs.
- [SelectivePrefetcherDisabling.scala](proteus/src/main/scala/riscv/plugins/SelectivePrefetcherDisabling.scala) is the plugin of the Selective Disabling defense, which uses:
- [SecurityController.scala](proteus/src/main/scala/riscv/plugins/SecurityController.scala) to change the security mode through CSRs (DMPs are enabled when the security mode is OFF).
- When the SecDmp or the SelectivePrefetcherDisabling plugin is used in a processor configuration (bottom of [Core.scala](proteus/src/main/scala/riscv/Core.scala)) , it modifies logic inside of the Cache to apply the defense at the time that the processor is being built, see [Cache.scala](proteus/src/main/scala/riscv/plugins/Cache.scala)

We additionally made the [SecretPartitionChecker.scala](proteus/src/main/scala/riscv/plugins/SecretPartitionChecker.scala) plugin, which modifies the [Lsu](proteus/src/main/scala/riscv/plugins/memory/Lsu.scala) to throw an exception when secret-tainted data is written to public memory, to verify the static secret partition correctness for programs that do not intentionally declassify secrets.

# Setup (+- 20 minutes)
You can either use Docker, or set up everything locally; for the local setup, the given commands work on Linux Mint, Ubuntu or similar

The installation takes around 20 minutes, and requires 20 GB free space during installation (including the space taken up by docker's build cache)

## Docker (recommended)
Instead of installing everything manually, you can use the provided [Dockerfile](Dockerfile):

First create the results directory (optional, but this ensures the directory is owned by you and not docker)
```
mkdir -p results
```

Then build and run the docker image (run the docker commands with **`sudo`** in front if you get permission denied errors)

```
docker compose run --name secdmp secdmp
```

When the build completes, you end up in a shell in which you can run the evaluation by executing the commands of the next sections

You can leave the container with `exit` and reopen it later with:
```
docker start -ai secdmp
```

The container keeps everything you build inside it, except the results of the evaluation and the generated figures and tables, which are written to the `results` directory both inside the container and on the host machine

### Note: Preventing System Sleep
When intending to replicate (parts of) the evaluation on a laptop, it is recommended to add the following in front of the `docker compose run` and `docker start` commands to prevent the system from going to sleep when leaving the evaluation running unattended:

```
systemd-inhibit --what=idle:sleep
```

## Local Setup
To install it locally, simply mirror the installation steps of the [Dockerfile](Dockerfile), installing the required basic dependencies, the RISC-V toolchain (release 2026.01.01, make sure to add the toolchain to your path after installing), EVAL-HD, Sbt, and setting up the virtual python environment

# Minimal Working Example (+- 1 minute)
You can run a minimal example and verify whether everything installed correctly by running:

```
./verify_installation.sh
```

# Running the evaluation
Follow the steps below to run the evaluation. You can either build the processors, compile the benchmarks and run each evaluation separately, or use the provided wrapper script to run everything with one command.
The entire evaluation can take up to 17 hours.
All reported timings were measured on a laptop with 16 cores and 64GB RAM

The hardware evaluation takes the longest (8 hours), as the amount of parallelization possible for the hardware evaluation is restricted by the amount of available RAM. The DMP-Bench performance evaluation is the second-longest, which takes 6 hours as it executes 2240 runs: 20 work/crypto combinations x 4 work percentage variations x the 4 DMPs x the 7 processor configurations (the 6 prototypes + standalone partitioning cost)

**Collecting and Comparing Results**
- All generated results, figures and tables are saved in the `results` directory
- We provide the expected output in the [expected_results](expected_results/) directory 
- When using the recommended docker setup, all results should be an identical match to [expected_results](expected_results/) except for the hardware evaluation results, which can slightly (negligibly) fluctuate

## Running the Entire Evaluation

This script simply executes each of the commands listed below in order

```
./run_secdmp_eval.sh
```

## Building the Processor Simulations (+- 60 minutes)
To build the processor simulations of the Proteus+DMP baseline and defenses for each DMP, run:
```
./build_processor_sims.sh
```

## Compiling Benchmarks (+- 15 minutes)
```
make
```
This compiles all benchmarks, which can take up to 15 minutes

(To only build a select benchmark, run one of the following commands:
`make dmp_tests`, `make spectre_tests`, `make dmp_bench`, `make embench`, `make hacl_crypto`, `make array_of_pointers`, `make spmv`, `make coremark`)

## Security Evaluation (+- 20 minutes)
The following command runs the DMP and Spectre security evaluation for Proteus+DMP, permanent disabling, selective disabling, SecDMP, ProSpeCT and ProSpeCT+SecDMP, for each DMP.

```
source .venv/bin/activate && python3 security_eval.py ; deactivate
```
This activates the virtual environment, runs the evaluation and deactivates the virtual environment

The results are logged in `results/security_evaluation`

## Performance Evaluation
The following sections explain how to run the HACL* crypto, Embench, CoreMark, Array of Pointers, SpMV and DMP-Bench performance evaluation for Proteus+DMP, permanent disabling, selective disabling, SecDMP, ProSpeCT and ProSpeCT+SecDMP (and the Partitioning with no defense applied where relevant), for each DMP.

### Hacl* Crypto (+- 2 minutes)
Run the HACL* crypto performance evaluation with:
```
python3 performance_eval_hacl_crypto.py
```
After completion, results are logged in `results/performance_evaluation/hacl_crypto`

To verify the correctness of the secret partitioning through annotations (i.e., that no secrets spill), run the following.
If no exceptions are printed, it means there is no spillage and the partitioning is correct.
```
./check_crypto_partition.sh
```

### Embench (+- 1 hours 40 minutes)
Run the Embench performance evaluation with:
```
./performance_eval_embench.sh
```
After completion, results are logged in `results/performance_evaluation/embench`

### CoreMark (+- 1 minute)
Run the CoreMark performance evaluation with:
```
./performance_eval_coremark.sh
```
After completion, results are logged in `results/performance_evaluation/coremark`

### Array of Pointers (+- 15 minutes)
Run the Array of Pointers performance evaluation with:
```
./performance_eval_array_of_pointers.sh
```
After completion, results are logged in `results/performance_evaluation/array_of_pointers`

### SpMV (+- 3 minutes)
Run the SpMV performance evaluation with:
```
./performance_eval_spmv.sh
```
After completion, results are logged in `results/performance_evaluation/spmv`

### DMP Bench (+- 6 hours)
Run the DMP Bench performance evaluation with:
```
python3 performance_eval_dmp_bench.py
```
After completion, results are logged in `results/performance_evaluation/dmp_bench`

## Hardware Evaluation (+- 8 hours)
Run the hardware evaluation for all processors (Proteus+DMP, permanent disabling, selective disabling, SecDMP, ProSpeCT, ProSpeCT+SecDMP, for each of the 4 DMPs) with:

```
./hardware_eval.sh
```
The results are logged in `results/hardware_evaluation`

## Generating Figures and Tables
After collecting all results, you can run the scripts to generate figures and tables, which will be saved in the `results` folder:

HACL* performance evaluation figures:
```
python3 plot_figures_hacl_crypto.py
```

Work functions figures (Embench, CoreMark, AoP, SpMV):
```
python3 plot_figures_work.py
```

DMP-Bench figures:
```
python3 plot_figures_dmp_bench.py
```

Tables (performance and hardware evaluation):
```
python3 generate_tables.py
```