#define DEBUG
#define DEBUG2
#include "solo5fpga.hpp"

// #include <hw/pci.hpp>
// #include <fs/common.hpp>
#include <cassert>
#include <stdlib.h>

#include <statman>

extern "C" {
#include <solo5.h>
}

Solo5FPGA::Solo5FPGA()
  : hw::FPGA()
{
  // struct solo5_fpga_info fpgai;
  // solo5_fpga_info(&fpgai);
  // INFO("Solo5FPGA", "Funky Virt FPGA");
}


int Solo5FPGA::init(void* bs, size_t bs_len,
    void* wr_queue, size_t wr_len, void* rd_queue, size_t rd_len) {
  solo5_result_t res;

  // INFO("Solo5FPGA", "Entering init()... \n");

  struct solo5_fpgainit fpgainit;
  fpgainit.bs           = bs;
  fpgainit.bs_len       = bs_len;
  fpgainit.wr_queue     = wr_queue;
  fpgainit.wr_queue_len = wr_len;
  fpgainit.rd_queue     = rd_queue;
  fpgainit.rd_queue_len = rd_len;

  // res = solo5_fpga_info();
  res = solo5_fpga_init(&fpgainit);

  if (res != SOLO5_R_OK) {
    return -1;
  }

  return 0;
}

int Solo5FPGA::handle_requests(void)
{
  return solo5_fpga_handle_request();
}

int Solo5FPGA::free(void)
{
  return solo5_fpga_free();
}

// Unused
void Solo5FPGA::deactivate()
{
  INFO("Solo5FPGA", "deactivate");
}

#include <kernel/solo5_manager.hpp>

struct Autoreg_solo5fpga {
  Autoreg_solo5fpga() {
    Solo5_manager::register_fpga(&Solo5FPGA::new_instance);
  }
} autoreg_solo5fpga;
