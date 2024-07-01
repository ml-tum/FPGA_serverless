#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/device.h"
#include "object/memory.h"
#include "object/cmd_queue.h"

#include <iostream>

namespace funkycl {

static void * 
clEnqueueMapBuffer(cl_command_queue command_queue,
                   cl_mem           buffer,
                   cl_bool          blocking_map,
                   cl_map_flags     map_flags,
                   size_t           offset,
                   size_t           size,
                   cl_uint          num_events_in_wait_list,
                   const cl_event * event_wait_list,
                   cl_event *       event,
                   cl_int *         errcode_ret)
{
  auto f_memobj = cl_to_funkycl(buffer);

  auto meminfo = f_memobj->get_meminfo();
  if( (map_flags & CL_MAP_READ) && (meminfo->flags & CL_MEM_READ_ONLY))
  {
    std::cout << "Error: in " << __func__ << ", read-only host memory cannot be mapped to read-only buffer. " << std::endl;

    if(errcode_ret)
      *errcode_ret = CL_FALSE;
    return nullptr;
  }
    
  if( (map_flags & CL_MAP_WRITE) && (meminfo->flags & CL_MEM_WRITE_ONLY))
  {
    std::cout << "Error: in " << __func__ << ", write-only host memory cannot be mapped to write-only buffer. " << std::endl;

    if(errcode_ret)
      *errcode_ret = CL_FALSE;
    return nullptr;
  }

  if( f_memobj->get_host_ptr() != nullptr)
  {
    std::cout << "Error: in " << __func__ << ", host memory is already mapped to the buffer. " << std::endl;

    if(errcode_ret)
      *errcode_ret = CL_FALSE;
    return nullptr;
  }

  /* TODO: support offset */
  if(offset > 0)
    std::cout << "Warning: in " << __func__ << ", currently, offset is ignored in Funky." << std::endl;

  void* host_ptr = f_memobj->map_buffer(size);
  DEBUG_STREAM("host_mem (addr: " << std::hex << host_ptr << " has been mapped to buffer [" << f_memobj->get_id() << "].");

  if(errcode_ret)
    *errcode_ret = CL_SUCCESS;

  return host_ptr;
}

} // funkycl

CL_API_ENTRY void * CL_API_CALL
clEnqueueMapBuffer(cl_command_queue command_queue,
                   cl_mem           buffer,
                   cl_bool          blocking_map,
                   cl_map_flags     map_flags,
                   size_t           offset,
                   size_t           size,
                   cl_uint          num_events_in_wait_list,
                   const cl_event * event_wait_list,
                   cl_event *       event,
                   cl_int *         errcode_ret) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clEnqueueMapBuffer
    (command_queue, buffer, blocking_map, map_flags, offset, size, num_events_in_wait_list, event_wait_list, event, errcode_ret);
}

