#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/device.h"

namespace funkycl {

static cl_int
clRetainDevice(cl_device_id device)
{
  DEBUG_STREAM("Retain device");

  cl_to_funkycl(device)->retain();
  return CL_SUCCESS;
}

} // funkycl

CL_API_ENTRY cl_int CL_API_CALL
clRetainDevice(cl_device_id device) CL_API_SUFFIX__VERSION_1_2
{
  return funkycl::clRetainDevice(device);
}

