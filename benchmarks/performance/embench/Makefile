BSP_DIR = ../../../ecosystem/newlib-bsp
SRC_DIR ?= ./src

all:
	make -C $(BSP_DIR) $(BSP_LIB_NAME)
	scons --config-dir=proteusverilator \
	    cc=$(CC) \
	    cflags="$(CFLAGS)" \
	    ldflags="$(ARCHFLAGS) -T $(BSP_DIR)/link.ld -L$(BSP_DIR)" \
	    user_libs="-lm -lproteus" \
	    src=$(SRC_DIR) \
	    warmup_heat=0

clean:
	make -C $(BSP_DIR) clean
	rm -rf bd
	rm -f $(SRC_DIR)/*/*.o support/*.o

include $(BSP_DIR)/Makefile.include
