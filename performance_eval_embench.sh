#!/usr/bin/env bash
trap "kill 0" SIGINT

DMPs=(
    "AppleDmp"
    "IntelDmp"
    "Cdp"
    "Imp"
)

CORES=(
    "proteus_dmp"
    "permanent_disabling"
    "selective_disabling"
    "secdmp"
    "prospect"
    "prospect_secdmp"
)

cd benchmarks/performance/embench

SIM_BUILD_FOLDER=../../../ecosystem/simulation/build/sim
LOGDIR=../../../results/performance_evaluation/embench

echo Running evaluation for embench
echo

# run benchmarks in parallel
max_jobs=$(( $(nproc) * 3 / 4 > 0 ? $(nproc) * 3 / 4 : 1 ))
jobs=0
for dmp in "${DMPs[@]}"; do
    rm -rf $LOGDIR/$dmp
    mkdir -p $LOGDIR/$dmp
    for core in "${CORES[@]}"; do
        echo Evaluating $core with $dmp...
        (python3 benchmark_speed.py --target-module=run_proteus --timeout=5400 --absolute --logdir=$LOGDIR/$dmp --logfilename=$core --sim=$SIM_BUILD_FOLDER/$dmp/$core > /dev/null; echo Finished $core with $dmp) &
        ((jobs++))

        if (( jobs >= max_jobs )); then
            wait -n
            ((jobs--))
        fi
    done
done
wait

cd ../../../
echo Finished!
