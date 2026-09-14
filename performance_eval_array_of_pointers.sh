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

cd benchmarks/performance/array_of_pointers

SIM_BUILD_FOLDER=../../../ecosystem/simulation/build/sim
LOGDIR=../../../results/performance_evaluation/array_of_pointers

echo Running evaluation for array_of_pointers
echo
for dmp in "${DMPs[@]}"; do
    (
        mkdir -p $LOGDIR/$dmp
        > $LOGDIR/$dmp/array_of_pointers.txt
        for core in "${CORES[@]}"; do
            echo Evaluating $core with $dmp...
            {
                $SIM_BUILD_FOLDER/$dmp/$core array_of_pointers.bin 2>&1
            } \
            | grep 'Clock cycles:' \
            | sed "s/Clock cycles: /$core: /" \
            | sed "s/$/ cycles/" \
            >> $LOGDIR/$dmp/array_of_pointers.txt
            echo Finished $core with $dmp
        done
    ) &
done
wait
echo

cd ../../../
echo Finished!
