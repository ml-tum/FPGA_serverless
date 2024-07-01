#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/kernel.h"

namespace funkycl {

/* Kernel Object APIs */
static cl_kernel
clCreateKernel(cl_program      program,
               const char *    kernel_name,
               cl_int *        errcode_ret)
{
  auto kernel =
    std::make_unique<funkycl::kernel>(cl_to_funkycl(program), kernel_name);

  // TODO: How to check if the kernel exists in program?
  // submit a request to backend and receive a response if any error occurs??
  // e.g., program->get_device()->send_request(funky_msg::KERNEL, kernel_name);
  // This might cause performance overhead... 

  if(errcode_ret)
    *errcode_ret = CL_SUCCESS;

  DEBUG_STREAM("Create kernel [" << kernel->get_id() << "]: refcount=" << kernel->count());

  return kernel.release();
}

} // funkycl


CL_API_ENTRY cl_kernel CL_API_CALL
clCreateKernel(cl_program      program,
               const char *    kernel_name,
               cl_int *        errcode_ret) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clCreateKernel
    (program, kernel_name, errcode_ret);
}



