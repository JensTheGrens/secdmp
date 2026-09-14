BSP_DIR = ../../../ecosystem/newlib-bsp

MODE ?= 2
WORK_PERCENTAGE ?= 75
CRYPTO_BENCH ?= 0
WORK_BENCH ?= 0
DMP ?= 0

HACL_DIR = ../hacl_crypto
COREMARK_DIR = ../coremark
ARRAY_OF_POINTERS_DIR = ../array_of_pointers
SPMV_DIR = ../spmv
EMBENCH_DIR = ../embench
SGLIB_DIR = $(EMBENCH_DIR)/src/sglib-combined
EMBENCH_SUPPORT_DIR = $(EMBENCH_DIR)/support

ifneq ($(filter 2 3,$(MODE)),)
HACL_LIB_DIR = $(HACL_DIR)/annotated_hacl_primitives
KARAMEL_INCLUDE = $(HACL_DIR)/annotated_karamel/include
KARAMEL_LIB_INCLUDE = $(HACL_DIR)/annotated_karamel/krmllib/dist/minimal
else
HACL_LIB_DIR = $(HACL_DIR)/hacl_primitives
KARAMEL_INCLUDE = $(HACL_DIR)/karamel/include
KARAMEL_LIB_INCLUDE = $(HACL_DIR)/karamel/krmllib/dist/minimal
endif
HACL_LIB = $(HACL_LIB_DIR)/libhacl.a
EXTRA_OBJECTS += $(HACL_LIB)

EXTRA_CFLAGS = -I$(HACL_LIB_DIR) -I$(KARAMEL_INCLUDE) -I$(KARAMEL_LIB_INCLUDE)

ifeq ($(WORK_BENCH),0)
# sglib-combined
WORK_BENCH_DIR = $(SGLIB_DIR)
WORK_BENCH_OBJECTS = $(WORK_BENCH_DIR)/combined.o $(EMBENCH_SUPPORT_DIR)/beebsc.o
EXTRA_CFLAGS += -I$(EMBENCH_SUPPORT_DIR) -DGLOBAL_SCALE_FACTOR=1 -DLOCAL_SCALE_FACTOR=1
else ifeq ($(WORK_BENCH),1)
# coremark
WORK_BENCH_DIR = $(COREMARK_DIR)
WORK_BENCH_OBJECTS = $(addprefix $(WORK_BENCH_DIR)/, core_list_join.o core_matrix.o core_portme.o core_state.o core_util.o coremark_driver.o)
else ifeq ($(WORK_BENCH),2)
# array_of_pointers
WORK_BENCH_DIR = $(ARRAY_OF_POINTERS_DIR)
WORK_BENCH_OBJECTS = $(WORK_BENCH_DIR)/array_of_pointers_benchmark.o
else ifeq ($(WORK_BENCH),3)
# spmv
WORK_BENCH_DIR = $(SPMV_DIR)
WORK_BENCH_OBJECTS = $(WORK_BENCH_DIR)/spmv_benchmark.o
endif

EXTRA_CFLAGS += -I$(WORK_BENCH_DIR)

TARGET = dmp_bench
OUTPUT_FOLDER ?= .
OUTPUT_FILE_NAME ?= $(TARGET)

all: set_config hacl_lib $(TARGET).elf $(TARGET).bin
	if [ $(OUTPUT_FOLDER) != . ] || [ $(OUTPUT_FILE_NAME) != $(TARGET) ]; then \
		mkdir -p $(OUTPUT_FOLDER); \
		mv $(TARGET).elf $(OUTPUT_FOLDER)/$(OUTPUT_FILE_NAME).elf; \
		mv $(TARGET).bin $(OUTPUT_FOLDER)/$(OUTPUT_FILE_NAME).bin; \
	fi

set_config: local_clean
	sed -i "s/#define WORK_PERCENTAGE .*/#define WORK_PERCENTAGE $(WORK_PERCENTAGE)/" bench_config.h
	sed -i "s/#define CRYPTO_BENCH .*/#define CRYPTO_BENCH $(CRYPTO_BENCH)/" bench_config.h
	sed -i "s/#define WORK_BENCH .*/#define WORK_BENCH $(WORK_BENCH)/" bench_config.h
	sed -i "s/#define DMP .*/#define DMP $(DMP)/" bench_config.h

hacl_lib:
	make -C $(HACL_DIR) hacl_lib MODE=$(MODE)

$(TARGET).elf: $(WORK_BENCH_OBJECTS)

include $(BSP_DIR)/Makefile.include

clean:
	make -C $(BSP_DIR) clean
	make -C $(HACL_DIR) clean
	rm -f *.elf *.bin *.o

local_clean:
	rm -f $(TARGET).elf $(TARGET).bin
