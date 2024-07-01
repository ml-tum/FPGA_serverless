#include "device.h"

#include <iostream>
#include <vector>
#include <cstdlib>

namespace funkycl
{

device::device(platform* pltf) 
  : response_q(std::make_unique<buffer::Reader<funky_msg::response>>(FUNKY_MSG_QUEUE_MAX_ELEMS)),
    request_q(std::make_unique<buffer::Writer<funky_msg::request>>(FUNKY_MSG_QUEUE_MAX_ELEMS)),
    init_flag(false)
{
  m_platform = pltf;
}

void device::init_vfpga(std::vector<unsigned char>& bitstream)
{
  auto& vfpga = hw::Devices::fpga(0);

  // std::cout << "GUEST: sending fpga_init hypercall request..." << std::endl;

  /* do a hypercall */
  vfpga.init(bitstream.data(), bitstream.size(),
      request_q->get_baseaddr(), request_q->get_mmsize(),
      response_q->get_baseaddr(), response_q->get_mmsize());

  init_flag = true;
  return;
}

void 
device::free_vfpga()
{
  DEBUG_PRINT("release vFPGA.");
  auto& vfpga = hw::Devices::fpga(0);
  vfpga.free();

  init_flag = false;
  return;
}

bool 
device::is_initialized(void)
{
  return init_flag;
}

bool 
device::vfpga_send_request(funky_msg::request& req)
{
  DEBUG_STREAM("req: " << req.get_request_type() << ", addr:" << &req);

  if (req.get_request_type() == funky_msg::MEMORY)
  {
    int num;
    auto mems = (funky_msg::mem_info**) req.get_meminfo_array(num);
    auto mem = (funky_msg::mem_info*) mems[0];
    DEBUG_STREAM("Before pushing Memreq: addr=" << mem << ", num=" << num << ", index=" << mem->id << ", MemType=" << mem->type << ", flags=" << mem->flags << ", host_ptr=" << mem->src << ", size=" << mem->size);

  }

  auto ret = request_q->push(req);

  DEBUG_STREAM("num of queued requests: " << request_q->size());

  return ret;
}

funky_msg::response* 
device::vfpga_get_response()
{
  return response_q->pop();
}

int 
device::vfpga_handle_requests()
{
  auto& vfpga = hw::Devices::fpga(0);

  /* do a hypercall */
  return vfpga.handle_requests();
}

device::~device()
{
  // TODO: release cl_device objects
}


} // funkycl


