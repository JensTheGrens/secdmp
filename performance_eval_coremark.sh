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

cd benchmarks/performance/coremark

SIM_BUILD_FOLDER=../../../ecosystem/simulation/build/sim
LOGDIR=../../../results/performance_evaluation/coremark

echo Running evaluation for coremark
echo
for dmp in "${DMPs[@]}"; do
    (
        mkdir -p $LOGDIR/$dmp
        > $LOGDIR/$dmp/coremark.txt
        for core in "${CORES[@]}"; do
            echo Evaluating $core with $dmp...
            {
                $SIM_BUILD_FOLDER/$dmp/$core coremark.bin 2>&1
            } \
            | grep 'Clock cycles:' \
            | sed "s/Clock cycles: /$core: /" \
            | sed "s/$/ cycles/" \
            >> $LOGDIR/$dmp/coremark.txt
            echo Finished $core with $dmp
        done
    ) &
done
wait
echo

cd ../../../
echo Finished!
