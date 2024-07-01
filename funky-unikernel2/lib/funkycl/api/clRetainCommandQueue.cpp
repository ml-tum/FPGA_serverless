#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/cmd_queue.h"

namespace funkycl {

static cl_int
clRetainCommandQueue(cl_command_queue command_queue)
{
  cl_to_funkycl(command_queue)->retain();

  return CL_SUCCESS;
}

} // funkycl

CL_API_ENTRY cl_int CL_API_CALL
clRetainCommandQueue(cl_command_queue command_queue) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clRetainCommandQueue(command_queue);
}

