BSP_DIR = ../../../ecosystem/newlib-bsp

COREMARK_OBJECTS = core_list_join.o core_matrix.o core_portme.o core_state.o core_util.o coremark_driver.o

all: coremark.elf coremark.bin

coremark.elf: $(COREMARK_OBJECTS)

clean:
	make -C $(BSP_DIR) clean
	rm -f coremark.elf coremark.bin $(COREMARK_OBJECTS)

include $(BSP_DIR)/Makefile.include
