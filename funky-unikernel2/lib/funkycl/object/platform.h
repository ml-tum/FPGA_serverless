#ifndef __PLATFORM_H
#define __PLATFORM_H

#include <memory>
#include <vector>

#include "object.h"
#include "device.h"

namespace funkycl {
#define FUNKY_VFPGA_ID 1

class platform : public _cl_platform_id
{
public:
  platform();
  ~platform();

  static std::shared_ptr<platform> get_shared_platform();

  device* get_device();

private:
  // device* device;
  // One platform has one device object (vFPGA). Two or more vFPGAs will be attachable?  
  std::unique_ptr<device> m_device;

};

platform*
get_global_platform();

} // namespace funkycl



#endif // __PLATFORM_H

