#ifndef __CONTEXT_H
#define __CONTEXT_H

#include <memory>
#include <vector>

#include "config.h"
#include <CL/opencl.h>

#include "object.h"
#include "refcount.h"
#include "device.h"

namespace funkycl {
#define FUNKY_VFPGA_ID 1

class context : public _cl_context, public refcount
{
public:
  context(const cl_context_properties* properties
      ,size_t num_devices 
      ,const cl_device_id* devices
      );
      // ,const notify_action& notify=notify_action());

  context(platform* pltf);
  ~context();

  device*
  get_first_device() const
  {
    return (m_devices.size()==1)
      ? (*(m_devices.begin())).get()
      : nullptr;
  }

  device*
  get_device() const;

  /* for sending MEMORY requests to vfpga backend */
  void register_meminfo(funky_msg::mem_info* meminfo);

  size_t get_all_meminfo_size(void)
  {
    return meminfo_list.size();
  }

  void** load_all_meminfo_addr(void)
  {
    meminfo_list_update_flag = false;
    return (void **)(&meminfo_list[0]);
  }

  bool is_meminfo_list_updated(void)
  {
    return meminfo_list_update_flag;
  }

private:
  const cl_context_properties* m_props;
  std::vector<ptr<device>> m_devices;

  /* for sending MEMORY requests to vfpga backend */
  std::vector<funky_msg::mem_info*> meminfo_list; 
  bool meminfo_list_update_flag = false;
};

} // namespace funkycl


#endif // __CONTEXT_H

