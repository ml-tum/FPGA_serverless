#ifndef __DEVICE_H
#define __DEVICE_H

#include <memory>
#include <vector>

// #include <hw/fpga.hpp>
#include <hw/devices.hpp>

#include "object.h"
#include "refcount.h"
#include "platform.h"

#include <buffer.hpp>
#include <funky_msg.hpp>

namespace funkycl {
#define FUNKY_VFPGA_ID 1
#define FUNKY_MSG_QUEUE_MAX_ELEMS 128

class device : public _cl_device_id, public refcount
{
private:
  platform* m_platform;
  // hw::FPGA* vfpga; // = hw::Devices::fpga(0);
  bool init_flag;

  // TODO: FunkyCL command class
  std::unique_ptr<buffer::Reader<funky_msg::response>> response_q;
  std::unique_ptr<buffer::Writer<funky_msg::request>> request_q;

public:
  device(platform* pltf);
  ~device();

  void init_vfpga(std::vector<unsigned char>& bitstream);
  void free_vfpga(void);
  // void sync_vfpga(void);
  bool is_initialized(void);

  bool vfpga_send_request(funky_msg::request& req);
  funky_msg::response* vfpga_get_response(void);
  int vfpga_handle_requests(void);
};

// device* get_device();

} // namespace funkycl

#endif // __DEVICE_H

