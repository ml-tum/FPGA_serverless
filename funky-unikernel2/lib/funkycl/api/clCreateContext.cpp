#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/context.h"

#include <iostream>

namespace funkycl {

static cl_context
clCreateContext(const cl_context_properties * properties,
                cl_uint                       num_devices,
                const cl_device_id *          devices,
                void (CL_CALLBACK *  pfn_notify )(const char *, const void *, size_t, void *),
                void *user_data,
                cl_int *errcode_ret)
{
  // Duplicate devices are ignored
  std::vector<cl_device_id> vdevices (devices,devices+num_devices);
  std::sort(vdevices.begin(),vdevices.end());
  vdevices.erase(std::unique(vdevices.begin(),vdevices.end()),vdevices.end());

  // TODO: set a callback function
  auto context = std::make_unique<funkycl::context>(properties,vdevices.size(),&vdevices[0]);

  if(errcode_ret)
    *errcode_ret = CL_SUCCESS;

  return context.release();
}

} // funkycl

cl_context
clCreateContext(const cl_context_properties * properties,
                cl_uint                       num_devices,
                const cl_device_id *          device_list,
                void (CL_CALLBACK *  pfn_notify )(const char *, const void *, size_t, void *),
                void *user_data,
                cl_int *errcode_ret)
{

  return funkycl::clCreateContext
    (properties,num_devices,device_list,pfn_notify, user_data, errcode_ret);

}


