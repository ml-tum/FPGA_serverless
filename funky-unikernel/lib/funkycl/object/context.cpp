#include "context.h"

namespace funkycl
{


context::context(const cl_context_properties* properties
      ,size_t num_devices 
      ,const cl_device_id* devices
    ) : m_props(properties)
{
  // TODO: Ensure devices are available for current process

  // downcast from cl_context to funkycl::context
  std::transform(devices,devices+num_devices
      ,std::back_inserter(m_devices)
      ,[](cl_device_id dev) {
      return funkycl::cl_to_funkycl(dev);
      });

}

context::~context()
{
  // TODO: release cl_device objects
}

device*
context::get_device() const
{
  auto device = get_first_device();
  return device;
}

void 
context::register_meminfo(funky_msg::mem_info* meminfo)
{
  meminfo_list_update_flag = true;
  meminfo_list.push_back(meminfo);

  DEBUG_STREAM("register meminfo. addr: " << meminfo);
}

} // funkygl


