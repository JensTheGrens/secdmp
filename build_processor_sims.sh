#!/usr/bin/env bash

set -e

DMPs=(
    "AppleDmp"
    "IntelDmp"
    "Cdp"
    "Imp"
)

mkdir -p ecosystem/simulation/build/sim
mkdir -p ecosystem/simulation/build/core

# build permanent disabling separately
echo Building permanent DMP disabling defense...
make -C ecosystem/simulation CORE="riscv.CoreDynamicPermanentDmpDisabling" PROTEUS_DIR=../../proteus EXE_NAME=permanent_disabling
cp ecosystem/simulation/build/Core.v ecosystem/simulation/build/core/permanent_disabling.v
echo

# build the other processors for each DMP
for dmp in "${DMPs[@]}"; do
    mkdir -p ecosystem/simulation/build/sim/${dmp}
    mkdir -p ecosystem/simulation/build/core/${dmp}
    
    # for the performance evaluation, copy the sim of permanent disabling to each DMP sim folder
    cp ecosystem/simulation/build/permanent_disabling ecosystem/simulation/build/sim/${dmp}/permanent_disabling

    echo ${dmp}: building the Proteus+DMP insecure baseline...
    make -C ecosystem/simulation CORE="riscv.CoreDynamicProteusDmp ${dmp}" PROTEUS_DIR=../../proteus EXE_NAME=sim/${dmp}/proteus_dmp
    cp ecosystem/simulation/build/Core.v ecosystem/simulation/build/core/${dmp}/proteus_dmp.v
    echo

    echo ${dmp}: building selective DMP disabling defense...
    make -C ecosystem/simulation CORE="riscv.CoreDynamicSelectiveDmpDisabling ${dmp}" PROTEUS_DIR=../../proteus EXE_NAME=sim/${dmp}/selective_disabling
    cp ecosystem/simulation/build/Core.v ecosystem/simulation/build/core/${dmp}/selective_disabling.v
    echo

    echo ${dmp}: building SecDMP defense...
    make -C ecosystem/simulation CORE="riscv.CoreDynamicSecDmp ${dmp}" PROTEUS_DIR=../../proteus EXE_NAME=sim/${dmp}/secdmp
    cp ecosystem/simulation/build/Core.v ecosystem/simulation/build/core/${dmp}/secdmp.v
    echo

    echo ${dmp}: building ProSpeCT with the insecure DMP...
    make -C ecosystem/simulation CORE="riscv.CoreDynamicProSpeCTDmp ${dmp}" PROTEUS_DIR=../../proteus EXE_NAME=sim/${dmp}/prospect
    cp ecosystem/simulation/build/Core.v ecosystem/simulation/build/core/${dmp}/prospect.v
    echo

    echo ${dmp}: building ProSpeCT combined with SecDMP defense...
    make -C ecosystem/simulation CORE="riscv.CoreDynamicProSpeCTSecDmp ${dmp}" PROTEUS_DIR=../../proteus EXE_NAME=sim/${dmp}/prospect_secdmp
    cp ecosystem/simulation/build/Core.v ecosystem/simulation/build/core/${dmp}/prospect_secdmp.v
    echo
done

echo Building the secret partition checker...
make -C ecosystem/simulation CORE="riscv.CoreDynamicCheckPartition" PROTEUS_DIR=../../proteus EXE_NAME=sim/partcheck

echo Finished!
