BSP_DIR = ../../../ecosystem/newlib-bsp

C_FILES := $(shell find . -name '*.c')
ASM_FILES := $(shell find . -name '*.s')

BASENAMES := $(C_FILES:.c=) $(ASM_FILES:.s=)

ELF_FILES := $(addsuffix .elf, $(BASENAMES))
BIN_FILES := $(addsuffix .bin, $(BASENAMES))

all: $(ELF_FILES) $(BIN_FILES)

%.elf: %.s
	$(CC) $(ARCHFLAGS) -c -o $@ $<
	$(CC) $(ARCHFLAGS) -ffreestanding -nostdlib -T assembly.ld -o $@ $<

clean:
	make -C $(BSP_DIR) clean
	rm -f $(ELF_FILES) $(BIN_FILES)

include $(BSP_DIR)/Makefile.include
