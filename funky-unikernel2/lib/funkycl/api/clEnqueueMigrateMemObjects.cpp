#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/device.h"
#include "object/kernel.h"
#include "object/cmd_queue.h"
#include "object/event.h"

#include <iostream>

namespace funkycl {

static cl_int
clEnqueueMigrateMemObjects(cl_command_queue       command_queue,
                           cl_uint                num_mem_objects,
                           const cl_mem *         mem_objects,
                           cl_mem_migration_flags flags,
                           cl_uint                num_events_in_wait_list,
                           const cl_event *       event_wait_list,
                           cl_event *             event)
{
  auto cmd_queue = cl_to_funkycl(command_queue);

  /* send a MEMORY request every time when this function is called
   * TODO: send the request only if any memobj has been newly created 
   *       since the last time this function called 
   * */
  auto ret = cmd_queue->vfpga_send_memory_request();
  if(ret)
    DEBUG_STREAM("Memory creation request has been issued.");
  else
    DEBUG_STREAM("No memory request is issued. all memobjs are already initialized.");

  /* create a new event object for this command */
  if(event != nullptr)
  {
    auto new_event =
      std::make_unique<funkycl::event>(cmd_queue, cmd_queue->get_context(), CL_COMMAND_MIGRATE_MEM_OBJECTS);
    *event = new_event.release();
  }

  /* if any argument regarding event objects exists, create an event info in cmd_queue class. */
  funky_msg::event_info* einfo=nullptr;
  if(event != nullptr || event_wait_list != nullptr)
  {
    /* if event_id == -1, no event object is assigned to this command (request) */
    int event_id = (event!=nullptr)? cl_to_funkycl(*event)->get_id(): -1;
    einfo = cmd_queue->create_event_info(event_id, num_events_in_wait_list, event_wait_list);
    DEBUG_STREAM("create event_info: id: " << event_id << ", num_events: " << num_events_in_wait_list);
  }

  /* send a "TRANSFER" request to backend */
  cmd_queue->vfpga_send_transfer_request(cmd_queue->get_id(), num_mem_objects, mem_objects, flags, einfo);

  return CL_SUCCESS;
}

} // funkycl


CL_API_ENTRY cl_int CL_API_CALL
clEnqueueMigrateMemObjects(cl_command_queue       command_queue,
                           cl_uint                num_mem_objects,
                           const cl_mem *         mem_objects,
                           cl_mem_migration_flags flags,
                           cl_uint                num_events_in_wait_list,
                           const cl_event *       event_wait_list,
                           cl_event *             event) CL_API_SUFFIX__VERSION_1_2
{
  return funkycl::clEnqueueMigrateMemObjects
    (command_queue, num_mem_objects, mem_objects, flags, num_events_in_wait_list, event_wait_list, event);
}





