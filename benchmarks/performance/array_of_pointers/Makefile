BSP_DIR = ../../../ecosystem/newlib-bsp

all: array_of_pointers.elf array_of_pointers.bin

array_of_pointers.elf: array_of_pointers_benchmark.o

clean:
	make -C $(BSP_DIR) clean
	rm -f array_of_pointers.elf array_of_pointers.bin array_of_pointers_benchmark.o

include $(BSP_DIR)/Makefile.include
