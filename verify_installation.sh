#!/usr/bin/env bash

set -e
cd "$(dirname "$0")" || exit 1

echo Verifying installation...

# check if the PATH contains opt/riscv/bin
if ! command -v riscv64-unknown-elf-gcc > /dev/null; then
    echo "Failed: the RISC-V toolchain is not in your PATH (add /opt/riscv/bin to your PATH)"
    exit 1
fi

# check if eval-hd directory exists
if [ ! -f eval-hd/freepdk-45nm/stdcells.lib ]; then
    echo "Failed: eval-hd is missing or was cloned without --recurse-submodules"
    exit 1
fi

# check if the python virtual environment exists, can be activated and has pyosys installed
if [ ! -f .venv/bin/activate ]; then
    echo "Failed: the python virtual environment directory is missing"
    exit 1
fi
source .venv/bin/activate
if ! OUTPUT=$(python3 -c "import pyosys, waveform_analysis" 2>&1); then
    echo "Failed: pyosys and waveform-analysis are not installed in .venv:"
    echo "$OUTPUT"
    exit 1
fi
deactivate

# build an in-order Proteus pipeline and make and run one benchmark
if ! OUTPUT=$(make -C ecosystem/simulation PROTEUS_DIR=../../proteus EXE_NAME=test_sim 2>&1); then
    echo Failed building Proteus:
    echo "$OUTPUT"
    exit 1
fi

if ! OUTPUT=$(make coremark 2>&1); then
    echo Failed compiling the test benchmark:
    echo "$OUTPUT"
    exit 1
fi

# run the test benchmark on proteus
if ! OUTPUT=$(./ecosystem/simulation/build/test_sim benchmarks/performance/coremark/coremark.bin 2>&1) \
    || ! grep -q "Clock cycles:" <<< "$OUTPUT" \
    || ! grep -q "RET=0" <<< "$OUTPUT"; then
    echo Failed running the test benchmark:
    echo "$OUTPUT"
    exit 1
fi

echo
echo Installation verified!
