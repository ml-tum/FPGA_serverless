#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/cmd_queue.h"

namespace funkycl {

static cl_int
clReleaseCommandQueue(cl_command_queue command_queue)
{
  if (cl_to_funkycl(command_queue)->release())
    delete cl_to_funkycl(command_queue);

  return CL_SUCCESS;
}

} // funkycl

cl_int
clReleaseCommandQueue(cl_command_queue command_queue)
{
  return funkycl::clReleaseCommandQueue(command_queue);
}


