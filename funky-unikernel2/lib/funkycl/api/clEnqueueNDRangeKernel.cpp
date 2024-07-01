#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/device.h"
#include "object/kernel.h"
#include "object/cmd_queue.h"
#include "object/event.h"

namespace funkycl {

/* Kernel Object APIs */
static cl_int
clEnqueueNDRangeKernel(cl_command_queue command_queue,
                       cl_kernel        kernel,
                       cl_uint          work_dim,
                       const size_t *   global_work_offset,
                       const size_t *   global_work_size,
                       const size_t *   local_work_size,
                       cl_uint          num_events_in_wait_list,
                       const cl_event * event_wait_list,
                       cl_event *       event)
{
  auto cmd_queue = cl_to_funkycl(command_queue);

  auto ret = cmd_queue->vfpga_send_memory_request();

  // if(work_dim != 1)
  // {
  //   std::cout << "Error: Funky does not support the work dimension greater than 1. Aborted. " << std::endl;
  //   return CL_FALSE;
  // }

  // if( (global_work_offset[0] != 0) || (global_work_size[0] != 1) || (local_work_size[0] != 1))
  // {
  //   std::cout << "Error: Funky only supports {g_work_offset, g_work_size, l_work_size} = {0, 1, 1}. Aborted." << std::endl;
  //   return CL_FALSE;
  // }

  /* create a new event object for this command */
  if(event != nullptr)
  {
    auto new_event =
      std::make_unique<funkycl::event>(cmd_queue, cmd_queue->get_context(), CL_COMMAND_NDRANGE_KERNEL);
    *event = new_event.release();
  }

  /* if any argument regarding event objects exists, create an event info in cmd_queue class. */
  funky_msg::event_info* einfo=nullptr;
  if(event != nullptr || event_wait_list != nullptr)
  {
    /* if event_id == -1, no event object is assigned to this command (request) */
    int event_id = (event!=nullptr)? cl_to_funkycl(*event)->get_id(): -1;
    einfo = cmd_queue->create_event_info(event_id, num_events_in_wait_list, event_wait_list);
  }

  /* enqueue an execution object */
  const size_t ndrange_ptr[3] = {*global_work_offset, *global_work_size, *local_work_size};
  cmd_queue->vfpga_send_exec_request(cmd_queue->get_id(), kernel, ndrange_ptr, einfo);

  return CL_SUCCESS;
}

} // funkycl


CL_API_ENTRY cl_int CL_API_CALL
clEnqueueNDRangeKernel(cl_command_queue command_queue,
                       cl_kernel        kernel,
                       cl_uint          work_dim,
                       const size_t *   global_work_offset,
                       const size_t *   global_work_size,
                       const size_t *   local_work_size,
                       cl_uint          num_events_in_wait_list,
                       const cl_event * event_wait_list,
                       cl_event *       event) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clEnqueueNDRangeKernel
    (command_queue, kernel, work_dim, global_work_offset, global_work_size, local_work_size, num_events_in_wait_list, event_wait_list, event);
}




