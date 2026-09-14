#pragma once

// `MODE` can be:
// 0 (default)
// 1 (security_modes for selective disabling)
// 2 (secret_partitioning for SecDMP and ProSpeCT)
// 3 (secret_partitioning_no_csr for running the partitioning on processors that don't support writing the region boundaries into CSRs)
#define MODE 3

#if MODE == 0
    #define MODE_NAME "default"
#elif MODE == 1
    #define MODE_NAME "security modes"
#elif MODE == 2
    #define MODE_NAME "secret partitioning"
#elif MODE == 3
    #define MODE_NAME "secret partitioning without csr writes"
#endif
