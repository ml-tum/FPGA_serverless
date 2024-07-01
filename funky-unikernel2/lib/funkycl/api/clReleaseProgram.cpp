#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/program.h"

namespace funkycl {

static cl_int
clReleaseProgram(cl_program program)
{
  DEBUG_STREAM("decrement refcount of program");

  if (cl_to_funkycl(program)->release())
  {
    DEBUG_STREAM("destroy program!");
    delete cl_to_funkycl(program);
  }

  return CL_SUCCESS;
}

} // funkycl

cl_int
clReleaseProgram(cl_program program)
{
  return funkycl::clReleaseProgram(program);
}


