#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/device.h"

namespace funkycl {

static cl_int
clReleaseDevice(cl_device_id device)
{
  DEBUG_STREAM("decrement refcount. ");

  if (cl_to_funkycl(device)->release())
  {
    DEBUG_STREAM("destroy device!");
    delete cl_to_funkycl(device);
  }

  return CL_SUCCESS;
}

} // funkycl

cl_int
clReleaseDevice(cl_device_id device)
{
  return funkycl::clReleaseDevice(device);
}


