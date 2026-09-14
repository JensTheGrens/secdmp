BSP_DIR = ../../../ecosystem/newlib-bsp

MODE ?= 2

NORMAL_HACL_PRIMITIVES_DIR = hacl_primitives
ANNOTATED_HACL_PRIMITIVES_DIR = annotated_hacl_primitives

ifneq ($(filter 2 3,$(MODE)),)
KARAMEL_INCLUDE = annotated_karamel/include
KARAMEL_LIB_INCLUDE = annotated_karamel/krmllib/dist/minimal
HACL_PRIMITIVES_DIR = $(ANNOTATED_HACL_PRIMITIVES_DIR)
else
KARAMEL_INCLUDE = karamel/include
KARAMEL_LIB_INCLUDE = karamel/krmllib/dist/minimal
HACL_PRIMITIVES_DIR = $(NORMAL_HACL_PRIMITIVES_DIR)
endif

EXTRA_CFLAGS = -I$(HACL_PRIMITIVES_DIR) -I$(KARAMEL_INCLUDE) -I$(KARAMEL_LIB_INCLUDE)

SRC_FILES = $(wildcard *.c)
HACL_SRC = $(wildcard $(HACL_PRIMITIVES_DIR)/*.c)

TARGETS := $(SRC_FILES:.c=)
HACL_PRIMITIVES := $(HACL_SRC:.c=)

ELF_TARGETS := $(addsuffix .elf, $(TARGETS))
BIN_TARGETS := $(addsuffix .bin, $(TARGETS))

HACL_OBJECTS := $(addsuffix .o, $(HACL_PRIMITIVES))
HACL_LIB := $(HACL_PRIMITIVES_DIR)/libhacl.a
EXTRA_OBJECTS += $(HACL_LIB)

OUTPUT_FOLDER ?= .

all: set_config $(ELF_TARGETS) $(BIN_TARGETS)
	if [ $(OUTPUT_FOLDER) != . ]; then \
		mkdir -p $(OUTPUT_FOLDER); \
		for TARGET in $(TARGETS); do \
			mv $$TARGET.elf $(OUTPUT_FOLDER)/$$TARGET.elf; \
			mv $$TARGET.bin $(OUTPUT_FOLDER)/$$TARGET.bin; \
		done; \
	fi

set_config: local_clean
	sed -i "s/#define MODE .*/#define MODE $(MODE)/" config.h

patch_salsa20:
	$(CC) $(CFLAGS) -S $(HACL_PRIMITIVES_DIR)/Hacl_Salsa20.c -o $(HACL_PRIMITIVES_DIR)/Hacl_Salsa20.s
	sed -i "s/^[[:space:]]*sw[[:space:]]\+t0,[[:space:]]*28(sp)/addi x0, x0, 0/" $(HACL_PRIMITIVES_DIR)/Hacl_Salsa20.s
	$(CC) $(CFLAGS) -c $(HACL_PRIMITIVES_DIR)/Hacl_Salsa20.s -o $(HACL_PRIMITIVES_DIR)/Hacl_Salsa20.o

hacl_lib: set_config $(HACL_LIB)

$(HACL_LIB): $(HACL_OBJECTS)
ifneq ($(filter 2 3,$(MODE)),)
	make patch_salsa20
endif
	$(AR) rcs $@ $^

include $(BSP_DIR)/Makefile.include

clean: local_clean
	make -C $(BSP_DIR) clean

local_clean:
	rm -f *.elf *.bin
	rm -f $(NORMAL_HACL_PRIMITIVES_DIR)/*.o $(NORMAL_HACL_PRIMITIVES_DIR)/*.a $(NORMAL_HACL_PRIMITIVES_DIR)/*.s $(ANNOTATED_HACL_PRIMITIVES_DIR)/*.o $(ANNOTATED_HACL_PRIMITIVES_DIR)/*.a $(ANNOTATED_HACL_PRIMITIVES_DIR)/*.s
