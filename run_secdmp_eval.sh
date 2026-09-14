#!/usr/bin/env bash

set -e
cd "$(dirname "$0")" || exit 1

echo Running the SecDMP evaluation...

# build processor simulations
./build_processor_sims.sh

# compile benchmarks
make

# security evaluation
echo
echo Running security evaluation...
source .venv/bin/activate && python3 security_eval.py ; deactivate

# performance evaluation
echo Running HACL* performance evaluation...
python3 performance_eval_hacl_crypto.py
echo Checking correctness of the secret partitioning...
./check_crypto_partition.sh
./performance_eval_embench.sh
./performance_eval_coremark.sh
./performance_eval_array_of_pointers.sh
./performance_eval_spmv.sh
python3 performance_eval_dmp_bench.py

# hardware evaluation
./hardware_eval.sh

# generate figures and tables
echo
echo Generating figures and tables...
python3 plot_figures_hacl_crypto.py
python3 plot_figures_work.py
python3 plot_figures_dmp_bench.py
python3 generate_tables.py

echo Finished the SecDMP evaluation!
echo All results are logged in the results folder
