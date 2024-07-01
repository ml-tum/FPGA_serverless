#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/kernel.h"

namespace funkycl {

static cl_int
clReleaseKernel(cl_kernel kernel)
{
  DEBUG_STREAM("Release kernel [" << cl_to_funkycl(kernel)->get_id() << "]: refcount=" << cl_to_funkycl(kernel)->count()-1);

  if (cl_to_funkycl(kernel)->release())
  {
    DEBUG_STREAM("destroy kernel [" << cl_to_funkycl(kernel)->get_id() << "]!");
    delete cl_to_funkycl(kernel);
  }

  return CL_SUCCESS;
}

} // funkycl

CL_API_ENTRY cl_int CL_API_CALL
clReleaseKernel(cl_kernel   kernel) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clReleaseKernel(kernel);
}


