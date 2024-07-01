#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/kernel.h"

namespace funkycl {

static cl_int
clRetainKernel(cl_kernel kernel)
{
  DEBUG_STREAM("Retain kernel [" << cl_to_funkycl(kernel)->get_id() << "]: refcount=" << cl_to_funkycl(kernel)->count()+1);

  cl_to_funkycl(kernel)->retain();
  return CL_SUCCESS;
}

} // funkycl

CL_API_ENTRY cl_int CL_API_CALL
clRetainKernel(cl_kernel    kernel) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clRetainKernel(kernel);
}

