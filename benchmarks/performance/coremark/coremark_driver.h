#ifndef COREMARK_DRIVER_H
#define COREMARK_DRIVER_H

void initialise_benchmark(void);
void warm_caches(int heat);
int benchmark(void);
int verify_benchmark(int r);

#endif
