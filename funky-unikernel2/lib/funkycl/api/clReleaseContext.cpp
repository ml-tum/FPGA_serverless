#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/context.h"

namespace funkycl {

static cl_int
clReleaseContext(cl_context  context )
{
  if (cl_to_funkycl(context)->release())
    delete cl_to_funkycl(context);

  return CL_SUCCESS;
}


} // funkycl


cl_int
clReleaseContext(cl_context context)
{
  return funkycl::clReleaseContext(context);
}


