
#include "kernel.h"

int solo5_serverless_test(void)
{
  ukvm_do_hypercall(UKVM_HYPERCALL_SERVERLESS_TEST, NULL);
  return 0;
}

solo5_result_t solo5_serverless_set_csr(uint32_t offset, uint64_t value)
{
  struct ukvm_serverless_set_csr set_csr;
  set_csr.offset = offset;
  set_csr.value = value;
  set_csr.ret = 1;

  ukvm_do_hypercall(UKVM_HYPERCALL_SERVERLESS_SET_CSR, &set_csr);

  return (set_csr.ret == 0) ? SOLO5_R_OK : SOLO5_R_EUNSPEC;
}

solo5_result_t solo5_serverless_load_bitstream(uint32_t config)
{
  struct ukvm_serverless_load_bitstream load_bitstream;
  load_bitstream.config = config;
  load_bitstream.ret = 1;

  ukvm_do_hypercall(UKVM_HYPERCALL_SERVERLESS_LOAD_BITSTREAM, &load_bitstream);

  return (load_bitstream.ret == 0) ? SOLO5_R_OK : SOLO5_R_EUNSPEC;
}

solo5_result_t solo5_serverless_map_memory(void *addr, size_t len, size_t input_len, size_t output_len)
{
  struct ukvm_serverless_map_memory map_memory;
  map_memory.addr = addr;
  map_memory.len = len;
  map_memory.input_len = input_len;
  map_memory.output_len = output_len;
  map_memory.ret = 1;

  ukvm_do_hypercall(UKVM_HYPERCALL_SERVERLESS_MAP_MEMORY, &map_memory);

  return (map_memory.ret == 0) ? SOLO5_R_OK : SOLO5_R_EUNSPEC;
}

solo5_result_t solo5_serverless_exec(void)
{
  struct ukvm_serverless_exec exec;
  exec.ret = 1;

  ukvm_do_hypercall(UKVM_HYPERCALL_SERVERLESS_EXEC, &exec);

  return (exec.ret == 0) ? SOLO5_R_OK : SOLO5_R_EUNSPEC;
}