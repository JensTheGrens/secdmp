FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

ENV LANG=C.UTF-8

WORKDIR /secdmp

# Proteus basic dependencies
RUN apt-get update && apt-get -yqq install build-essential git openjdk-17-jdk verilator libz-dev python3-pip python3-venv scons python3-matplotlib python3-numpy

# Install the RISC-V toolchain
# We use release version 2026.01.01 of the toolchain to ensure that all leakage tests and the Salsa20 assembly patch work correctly
RUN apt-get update && apt-get -yqq install autoconf automake autotools-dev curl python3 libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev libexpat-dev ninja-build

RUN git clone --branch 2026.01.01 --depth 1 --shallow-submodules https://github.com/riscv/riscv-gnu-toolchain.git /riscv-gnu-toolchain-temporary-installation && cd /riscv-gnu-toolchain-temporary-installation && sed -i -e 's#url = https://github.com/bminor/binutils-gdb.git#url = git://sourceware.org/git/binutils-gdb.git#' -e 's#url = https://github.com/bminor/glibc.git#url = git://sourceware.org/git/glibc.git#' -e 's#url = https://github.com/bminor/newlib.git#url = git://sourceware.org/git/newlib-cygwin.git#' .gitmodules && ./configure --prefix=/opt/riscv --with-cmodel=medany --with-multilib-generator="rv32im_zicsr_zicond-ilp32--;rv64im_zicsr_zicond-lp64--" --enable-debug-info && make -j$(nproc) && rm -rf /riscv-gnu-toolchain-temporary-installation

ENV PATH=/opt/riscv/bin:$PATH

# Hardware evaluation installation
RUN git clone --recurse-submodules --depth 1 --shallow-submodules https://github.com/KULeuven-COSIC/eval-hd.git

COPY ./ecosystem ./ecosystem
COPY ./benchmarks ./benchmarks
COPY ./expected_results ./expected_results
COPY ./proteus ./proteus
COPY Makefile README.md LICENSE ./
COPY ./*.sh ./*.py ./

# Make the scripts executable
RUN chmod +x ./*.sh ./*.py ./ecosystem/install-scripts/*.sh

# Sbt
RUN ./ecosystem/install-scripts/sbt.sh

# Python virtual environment setup
RUN python3 -m venv .venv && .venv/bin/pip install -e ecosystem/waveform-analysis && .venv/bin/pip install pyosys==0.64

CMD ["/bin/bash"]
