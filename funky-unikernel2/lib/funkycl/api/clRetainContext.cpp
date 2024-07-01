#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/context.h"

namespace funkycl {

static cl_int
clRetainContext(cl_context context)
{
  cl_to_funkycl(context)->retain();
  return CL_SUCCESS;
}

} // funkycl

CL_API_ENTRY cl_int CL_API_CALL
clRetainContext(cl_context context) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clRetainContext(context);
}

