BSP_DIR = ../../../ecosystem/newlib-bsp

MODE ?= DEFAULT
EXP_NUMBER ?= 0
EXP = EXP$(EXP_NUMBER)
OUTPUT_FOLDER ?= $(MODE)

BASENAMES := pht_load pht_store pht_branch pht_jump pht_division

ELF_FILES := $(addsuffix .elf, $(BASENAMES))
BIN_FILES := $(addsuffix .bin, $(BASENAMES))

all: semi_clean dirs $(ELF_FILES) $(BIN_FILES)
	@for base in $(BASENAMES); do \
		mv $${base}.elf $(OUTPUT_FOLDER)/$${base}_$(EXP_NUMBER).elf; \
		mv $${base}.bin $(OUTPUT_FOLDER)/$${base}_$(EXP_NUMBER).bin; \
	done

%.elf: %.S
	$(CC) $(ARCHFLAGS) -E -D$(MODE) -D$(EXP) lib.S > lib.s
	$(CC) $(ARCHFLAGS) -D$(MODE) -D$(EXP) -c $< -o $*.o
	$(CC) $(ARCHFLAGS) -ffreestanding -nostdlib -T assembly.ld -o $@ $*.o

dirs:
	@mkdir -p $(OUTPUT_FOLDER)

clean:
	make -C $(BSP_DIR) clean
	rm -f $(ELF_FILES) $(BIN_FILES) lib.s *.o

semi_clean:
	rm -f lib.s *.o

include $(BSP_DIR)/Makefile.include
