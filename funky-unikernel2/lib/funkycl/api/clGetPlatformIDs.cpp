#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/platform.h"

namespace funkycl {

static cl_int 
clGetPlatformIDs(cl_uint          num_entries,
                 cl_platform_id * platforms,
                 cl_uint *        num_platforms) 
{
  auto platform = get_global_platform();

  if (num_entries && platforms)
    platforms[0] = platform;

  if (num_platforms)
    *num_platforms = platform ? 1 : 0;

  return CL_SUCCESS;
}

} // funkycl

CL_API_ENTRY cl_int CL_API_CALL
clGetPlatformIDs(cl_uint          num_entries,
                 cl_platform_id * platforms,
                 cl_uint *        num_platforms) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clGetPlatformIDs
    (num_entries, platforms, num_platforms);
}

