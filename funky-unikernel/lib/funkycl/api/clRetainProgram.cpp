#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/program.h"

namespace funkycl {

static cl_int
clRetainProgram(cl_program program)
{
  DEBUG_STREAM("Retain program");

  cl_to_funkycl(program)->retain();
  return CL_SUCCESS;
}

} // funkycl

CL_API_ENTRY cl_int CL_API_CALL
clRetainProgram(cl_program program) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clRetainProgram(program);
}

