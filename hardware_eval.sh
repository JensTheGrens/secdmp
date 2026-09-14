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
    "selective_disabling"
    "secdmp"
    "prospect"
    "prospect_secdmp"
)

source .venv/bin/activate
cd eval-hd

# calculate number of parallel processes, making sure it does not use up all ram and crash the system
total_ram_gb=$(free -g | awk '/Mem:/{print $2}')
max_jobs_ram=$(( (total_ram_gb - 3) / 6 ))
max_jobs_cpu=$(( $(nproc) * 3 / 4 ))
if [ "$max_jobs_ram" -lt "$max_jobs_cpu" ]; then
    max_jobs=$max_jobs_ram
else
    max_jobs=$max_jobs_cpu
fi
max_jobs=$(( max_jobs > 0 ? max_jobs : 1 ))
echo "Running hardware evaluation on $max_jobs parallel processes"

jobs=0

# evaluate permanent disabling separately
LOGDIR="../results/hardware_evaluation"
mkdir -p $LOGDIR
{
    python -u ./eval-hd.py ../ecosystem/simulation/build/core/permanent_disabling.v --cell-library freepdk-45nm/stdcells.lib --maximum-target 16000
} \
| tee $LOGDIR/permanent_disabling.txt \
| sed "s/^/permanent_disabling: /" &
((jobs++))

if (( jobs >= max_jobs )); then
    wait -n
    ((jobs--))
fi

# evaluate the other processors for each DMP
for dmp in "${DMPs[@]}"; do
    mkdir -p $LOGDIR/$dmp
    for core in "${CORES[@]}"; do
        {
            python -u ./eval-hd.py ../ecosystem/simulation/build/core/$dmp/$core.v --cell-library freepdk-45nm/stdcells.lib --maximum-target 16000
        } \
        | tee $LOGDIR/$dmp/$core.txt \
        | sed "s/^/$dmp: $core: /" &
        ((jobs++))

        if (( jobs >= max_jobs )); then
            wait -n
            ((jobs--))
        fi
    done
done
wait

cd ..
deactivate
echo Finished!
