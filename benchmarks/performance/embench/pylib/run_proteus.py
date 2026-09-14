#!/usr/bin/env python3

# Python module to run programs on Proteus in a simulator.

# Copyright (C) 2019 Clemson University
#
# Contributor: Ola Jeppsson <ola.jeppsson@gmail.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Embench module to run benchmark programs.

This version is suitable for running programs natively.
"""

import argparse
import subprocess
import re
import pathlib

from embench_core import log
from embench_core import gp

def get_target_args(remnant):
    """Parse left over arguments"""
    parser = argparse.ArgumentParser(description='Get target specific args')

    parser.add_argument(
        '--sim',
        type=str,
        default=str(pathlib.Path(__file__).resolve().parents[3]/'simulation'/'build'/'sim'),
        help='Path to the Proteus simulation file',
    )

    parser.add_argument(
        '--riscv-prefix',
        type=str,
        default='riscv64-unknown-elf',
        help='Which prefix to use for the RISCV toolchain',
    )

    return parser.parse_args(remnant)

def decode_results(stdout_str, stderr_str):
    """Extract the results from the output string of the run. Return the
       elapsed time in milliseconds or zero if the run failed."""
    # See above in build_benchmark_cmd how we record the return value and
    # execution time. Return code is in standard output. Execution time is in
    # standard error.

    print(stdout_str)
    print(stderr_str)
    # Match "RET=rc"
    rcstr = re.search(r'^RET=(\d+)', stdout_str, re.S | re.M)
    if not rcstr:
        log.debug('Warning: Failed to find return code')
        return None

    # Match "Clock cycles: d"
    time = re.search(r'^Clock cycles: (\d+)', stdout_str, re.S | re.M)
    if time:
        cycles_elapsed = float(time.group(1))
        print(f"cycles: {cycles_elapsed}")
        # ms_elapsed = cycles_elapsed * (30 * 10e-6); # Critical path of 30 ns
        # ms_elapsed = cycles_elapsed * 30; # Critical path of 30 ns

        # this just returns the cycles for now, not ms because there is no one single Proteus CP, is different for each extension and changes on each update to the processor
        # but is ugly because the function says it returns ms so TODO: clean this up
        ms_elapsed = cycles_elapsed
        # Return value cannot be zero (will be interpreted as error)
        return max(float(ms_elapsed), 0.001)

    # We must have failed to find a time
    log.debug('Warning: Failed to find timing')
    return None

def run_benchmark(bench, path, args):
    """Runs the benchmark "bench" at "path". "args" is a namespace
       with target specific arguments. This function will be called
       in parallel unless if the number of tasks is limited via
       command line. "run_benchmark" should return the result in
       milliseconds.
    """

    # TODO: there has to be a better place to do this than here
    subprocess.run([f'{args.riscv_prefix}-objcopy', '-O', 'binary', path, f'{path}.bin'])

    try:
        res = subprocess.run(
            [f'{args.sim}', f'{path}.bin'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=gp['timeout']
        )
    except subprocess.TimeoutExpired:
        log.warning(f'Warning: Run of {bench} timed out.')
        return None
    if res.returncode != 0:
        return None
    return decode_results(res.stdout.decode('utf-8'), res.stderr.decode('utf-8'))
