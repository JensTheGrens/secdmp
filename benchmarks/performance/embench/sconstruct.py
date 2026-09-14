#!/usr/bin/env python3

# Script to build all benchmarks

# Copyright (C) 2017, 2024 Embecosm Limited
#
# Contributor: Konrad Moron <konrad.moron@tum.de>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
import os

def find_benchmarks(bd, env):
    src_dir = Path(env['src'])
    dir_iter = src_dir.iterdir()
    return ([Path(src_dir.name) / bench.name for bench in dir_iter if bench.is_dir()] + [env['dummy_benchmark']])

def parse_options():
    num_cpu = int(os.environ.get('NUM_CPU', 2))
    SetOption('num_jobs', num_cpu)
    AddOption('--build-dir', nargs=1, type='string', default='bd')
    AddOption('--config-dir', nargs=1, type='string', default='config2')
    config_dir = Path(GetOption('config_dir')).absolute()
    bd = Path(GetOption('build_dir')).absolute()

    vars = Variables(None, ARGUMENTS)
    print(ARGUMENTS)
    vars.Add('cc', default=env['CC'])
    vars.Add('cflags', default=env['CCFLAGS'])
    vars.Add('llcflags', default=[])
    vars.Add('ld', default=env['LINK'])
    vars.Add('ldflags', default=env['LINKFLAGS'])
    vars.Add('user_libs', default=[])
    vars.Add('warmup_heat', default=1,
             help='Number of iterations to warm up caches before measurements')
    vars.Add('gsf', default=1, help='Global scale factor')
    vars.Add('dummy_benchmark', default=(bd / 'support/dummy-benchmark'))
    vars.Add('llc', default='llc', help='Path to LLVM static compiler (llc)')
    vars.Add('src', default='src', help='Benchmark source dir')
    return vars

def setup_directories(bd, env, config_dir):
    src_dir = Path(env["src"])
    VariantDir(bd / src_dir.name, src_dir)
    VariantDir(bd / "support", "support")
    VariantDir(bd / "config", config_dir)
    SConsignFile(bd / ".sconsign.dblite")

def populate_build_env(env, vars):
    vars.Update(env)
    env.Append(CPPDEFINES={ 'WARMUP_HEAT' : '${warmup_heat}',
                            'GLOBAL_SCALE_FACTOR' : '${gsf}'})
    env.Append(CPPPATH=['support', config_dir])
    env.Replace(CCFLAGS = "${cflags}")
    env.Replace(LLCFLAGS = "${llcflags}")
    env.Replace(LINKFLAGS = "${ldflags}")
    env.Replace(CC = "${cc}")
    env.Replace(LINK = "${ld}")
    print(f"{env['user_libs']}".split())
    env.Prepend(LIBS = f"{env['user_libs']}".split())

def build_support_objects(env):
    support_objects = []
    support_objects += env.Object(str(bd / 'support/main.c'))
    support_objects += env.Object(str(bd / 'support/beebsc.c'))
    support_objects += env.Object(str(bd / 'config/boardsupport.c'))
    env.Default(support_objects)
    return support_objects

def add_ll_builder(env):
    llc = env['llc']
    llc_flags = env['llcflags']
    
    ll_builder = Builder(
        action=f'{llc} {llc_flags} -filetype=obj $SOURCE -o $TARGET',
        suffix='.o',
        src_suffix='.ll'
    )
    env.Append(BUILDERS={'LLCObject': ll_builder})


# MAIN BUILD SCRIPT
#env = DefaultEnvironment()
env = Environment(ENV=os.environ.copy())
vars = parse_options()

bd = Path(GetOption('build_dir')).absolute()
config_dir = Path(GetOption('config_dir')).absolute()

env.Replace(BUILD_DIR=bd)
env.Replace(CONFIG_DIR=config_dir)
populate_build_env(env, vars)
setup_directories(bd, env, config_dir)
add_ll_builder(env)

# Setup Help Text
env.Help("\nCustomizable Variables:", append=True)
env.Help(vars.GenerateHelpText(env), append=True)

support_objects = build_support_objects(env)
benchmark_paths = find_benchmarks(bd, env)

benchmark_objects = {}
for bench in benchmark_paths:
    print(bench)
    bench_dir = bd / bench / bench.name
    c_objects = env.Object(Glob(str(bd / bench / "*.c")))
    ll_files = Glob(str(bd / bench / "*.bc"))
    print(ll_files)
    ll_objects = [env.LLCObject(str(llf)) for llf in ll_files]

    all_objects = c_objects + ll_objects
    benchmark_objects[bench_dir] = all_objects

print(benchmark_objects)

env.Default(benchmark_objects.values())

for benchname, objects in benchmark_objects.items():
    bench_exe = env.Program(str(benchname), objects + support_objects)
    env.Default(bench_exe)
