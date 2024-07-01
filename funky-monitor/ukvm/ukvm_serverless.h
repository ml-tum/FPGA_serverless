
#ifndef UKVM_SERVERLESS_H
#define UKVM_SERVERLESS_H

#include "ukvm.h"

void serverless_connect();
void serverless_set_csr(uint32_t offset, uint64_t value);
void serverless_load_bitstream(uint32_t config);
void serverless_map_memory(void *addr, size_t len, size_t input_len, size_t output_len);
void serverless_exec();

#endif /* UKVM_SERVERLESS_H */

