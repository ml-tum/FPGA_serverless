#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/device.h"
#include "object/memory.h"

namespace funkycl {

/* Memory Object APIs */
static cl_mem 
clCreateBuffer(cl_context   context,
               cl_mem_flags flags,
               size_t       size,
               void *       host_ptr,
               cl_int *     errcode_ret)
{
  auto buffer =
    std::make_unique<funkycl::buffer>(cl_to_funkycl(context), flags, size, host_ptr);

  DEBUG_STREAM("Create buffer [" << buffer->get_id() << "]: refcount=" << buffer->count());
  DEBUG_STREAM("size: " << std::hex << size << ", addr: " << host_ptr << ", flags: " << flags);

  auto f_context = cl_to_funkycl(context);
  auto device = f_context->get_device();

  /* register meminfo in the context */
  f_context->register_meminfo(buffer->get_meminfo());
  DEBUG_STREAM("add new meminfo (num of memobjs: " << f_context->get_all_meminfo_size() << ")");

  if(errcode_ret)
    *errcode_ret = CL_SUCCESS;

  // auto ret = cmd_queue->vfpga_send_memory_request();

  return buffer.release();
}

} // funkycl


CL_API_ENTRY cl_mem CL_API_CALL
clCreateBuffer(cl_context   context,
               cl_mem_flags flags,
               size_t       size,
               void *       host_ptr,
               cl_int *     errcode_ret) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clCreateBuffer
    (context, flags, size, host_ptr, errcode_ret);
}


