DMP_SECURITY_DIR = benchmarks/security/dmp_tests
SPECTRE_SECURITY_DIR = benchmarks/security/spectre_tests

WORK_PERCENTAGES = 25 50 75 90
CRYPTO_BENCHES = 0 1 2 3 4
WORK_BENCHES = 0 1 2 3
DMPS = 0 1 2 3

DMP_BENCH_DIR = benchmarks/performance/dmp_bench
EMBENCH_DIR = benchmarks/performance/embench
HACL_CRYPTO_DIR = benchmarks/performance/hacl_crypto
ARRAY_OF_POINTERS_DIR = benchmarks/performance/array_of_pointers
SPMV_DIR = benchmarks/performance/spmv
COREMARK_DIR = benchmarks/performance/coremark

all: security performance

security: dmp_tests spectre_tests

performance: dmp_bench embench hacl_crypto array_of_pointers spmv coremark

dmp_tests:
	make -C $(DMP_SECURITY_DIR)

spectre_tests:
	make -C $(SPECTRE_SECURITY_DIR) MODE=DEFAULT EXP_NUMBER=0 OUTPUT_FOLDER=build/default
	make -C $(SPECTRE_SECURITY_DIR) MODE=DEFAULT EXP_NUMBER=1 OUTPUT_FOLDER=build/default
	make -C $(SPECTRE_SECURITY_DIR) MODE=SECURITY_MODES EXP_NUMBER=0 OUTPUT_FOLDER=build/security_modes
	make -C $(SPECTRE_SECURITY_DIR) MODE=SECURITY_MODES EXP_NUMBER=1 OUTPUT_FOLDER=build/security_modes
	make -C $(SPECTRE_SECURITY_DIR) MODE=SECRET_PARTITIONING EXP_NUMBER=0 OUTPUT_FOLDER=build/secret_partitioning
	make -C $(SPECTRE_SECURITY_DIR) MODE=SECRET_PARTITIONING EXP_NUMBER=1 OUTPUT_FOLDER=build/secret_partitioning

dmp_bench:
	@for work_p in $(WORK_PERCENTAGES); do \
		for crypto_bench in $(CRYPTO_BENCHES); do \
			for work_bench in $(WORK_BENCHES); do \
				for dmp in $(DMPS); do \
					make -C $(DMP_BENCH_DIR) MODE=0 WORK_PERCENTAGE=$${work_p} CRYPTO_BENCH=$${crypto_bench} WORK_BENCH=$${work_bench} DMP=$${dmp} OUTPUT_FILE_NAME=crypto$${crypto_bench}_work$${work_bench}_p$${work_p} OUTPUT_FOLDER=build/dmp$${dmp}/default; \
					make -C $(DMP_BENCH_DIR) MODE=1 WORK_PERCENTAGE=$${work_p} CRYPTO_BENCH=$${crypto_bench} WORK_BENCH=$${work_bench} DMP=$${dmp} OUTPUT_FILE_NAME=crypto$${crypto_bench}_work$${work_bench}_p$${work_p} OUTPUT_FOLDER=build/dmp$${dmp}/security_modes; \
					make -C $(DMP_BENCH_DIR) MODE=2 WORK_PERCENTAGE=$${work_p} CRYPTO_BENCH=$${crypto_bench} WORK_BENCH=$${work_bench} DMP=$${dmp} OUTPUT_FILE_NAME=crypto$${crypto_bench}_work$${work_bench}_p$${work_p} OUTPUT_FOLDER=build/dmp$${dmp}/secret_partitioning; \
					make -C $(DMP_BENCH_DIR) MODE=3 WORK_PERCENTAGE=$${work_p} CRYPTO_BENCH=$${crypto_bench} WORK_BENCH=$${work_bench} DMP=$${dmp} OUTPUT_FILE_NAME=crypto$${crypto_bench}_work$${work_bench}_p$${work_p} OUTPUT_FOLDER=build/dmp$${dmp}/secret_partitioning_no_csr; \
				done; \
			done; \
		done; \
	done

embench:
	make -C $(EMBENCH_DIR)

hacl_crypto:
	make -C $(HACL_CRYPTO_DIR) MODE=0 OUTPUT_FOLDER=build/default
	make -C $(HACL_CRYPTO_DIR) MODE=1 OUTPUT_FOLDER=build/security_modes
	make -C $(HACL_CRYPTO_DIR) MODE=2 OUTPUT_FOLDER=build/secret_partitioning
	make -C $(HACL_CRYPTO_DIR) MODE=3 OUTPUT_FOLDER=build/secret_partitioning_no_csr

array_of_pointers:
	make -C $(ARRAY_OF_POINTERS_DIR)

spmv:
	make -C $(SPMV_DIR)

coremark:
	make -C $(COREMARK_DIR)

clean:
	make -C $(DMP_SECURITY_DIR) clean
	make -C $(SPECTRE_SECURITY_DIR) clean
	make -C $(DMP_BENCH_DIR) clean
	make -C $(EMBENCH_DIR) clean
	make -C $(HACL_CRYPTO_DIR) clean
	make -C $(ARRAY_OF_POINTERS_DIR) clean
	make -C $(SPMV_DIR) clean
	make -C $(COREMARK_DIR) clean
	rm -rf $(DMP_BENCH_DIR)/build
	rm -rf $(HACL_CRYPTO_DIR)/build
	rm -rf $(SPECTRE_SECURITY_DIR)/build
