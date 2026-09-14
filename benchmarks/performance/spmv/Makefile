BSP_DIR = ../../../ecosystem/newlib-bsp

all: spmv.elf spmv.bin

spmv.elf: spmv_benchmark.o

clean:
	make -C $(BSP_DIR) clean
	rm -f spmv.elf spmv.bin spmv_benchmark.o

include $(BSP_DIR)/Makefile.include
