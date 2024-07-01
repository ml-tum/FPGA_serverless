#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/memory.h"

namespace funkycl {

static cl_int
clReleaseMemObject(cl_mem memobj)
{
  // DEBUG_STREAM("Release memobj [" << cl_to_funkycl(memobj)->get_id() << "]");
  DEBUG_STREAM("Release memobj [" << cl_to_funkycl(memobj)->get_id() << "]: refcount=" << cl_to_funkycl(memobj)->count()-1);

  if (cl_to_funkycl(memobj)->release())
  {
    DEBUG_STREAM("destroy memobj [" << cl_to_funkycl(memobj)->get_id() << "]!");
    delete cl_to_funkycl(memobj);
  }

  return CL_SUCCESS;
}

} // funkycl

CL_API_ENTRY cl_int CL_API_CALL
clReleaseMemObject(cl_mem memobj) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clReleaseMemObject(memobj);
}



