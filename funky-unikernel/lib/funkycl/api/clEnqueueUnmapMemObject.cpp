#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/device.h"
#include "object/memory.h"
#include "object/cmd_queue.h"

#include <iostream>

namespace funkycl {

static cl_int
clEnqueueUnmapMemObject(cl_command_queue command_queue,
                        cl_mem           memobj,
                        void *           mapped_ptr,
                        cl_uint          num_events_in_wait_list,
                        const cl_event * event_wait_list,
                        cl_event *       event)
{
  auto f_memobj = cl_to_funkycl(memobj);

  if(mapped_ptr != f_memobj->get_host_ptr())
  {
    std::cout << "Error: in " << __func__ << ", mapped_ptr is different from the actual pointer. " << std::endl;
    return CL_FALSE;
  }
    
  f_memobj->unmap_buffer();
  DEBUG_STREAM("host_mem mapped to buffer [" << f_memobj->get_id() << "] has been released. ");

  return CL_SUCCESS;
}

} // funkycl

CL_API_ENTRY cl_int CL_API_CALL
clEnqueueUnmapMemObject(cl_command_queue command_queue,
                        cl_mem           memobj,
                        void *           mapped_ptr,
                        cl_uint          num_events_in_wait_list,
                        const cl_event * event_wait_list,
                        cl_event *       event) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clEnqueueUnmapMemObject
    (command_queue, memobj, mapped_ptr, num_events_in_wait_list, event_wait_list, event);
}

