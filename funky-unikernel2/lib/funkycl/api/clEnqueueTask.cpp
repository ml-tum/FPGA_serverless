#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/device.h"
#include "object/kernel.h"
#include "object/cmd_queue.h"

namespace funkycl {


/* Kernel Object APIs */
static cl_int
clEnqueueTask(cl_command_queue  command_queue,
              cl_kernel         kernel,
              cl_uint           num_events_in_wait_list,
              const cl_event *  event_wait_list,
              cl_event *        event)
{
  const size_t global_work_offset[1]={0};
  const size_t global_work_size[1]={1};
  const size_t local_work_size[1]={1};

  return clEnqueueNDRangeKernel
    (command_queue, kernel, 1, global_work_offset, global_work_size, local_work_size,
     num_events_in_wait_list, event_wait_list, event);
}

} // funkycl


cl_int
clEnqueueTask(cl_command_queue  command_queue,
              cl_kernel         kernel,
              cl_uint           num_events_in_wait_list,
              const cl_event *  event_wait_list,
              cl_event *        event)
{
  return funkycl::clEnqueueTask
    (command_queue, kernel, num_events_in_wait_list, event_wait_list, event);
}




