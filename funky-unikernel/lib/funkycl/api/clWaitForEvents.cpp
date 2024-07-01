#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/device.h"
#include "object/cmd_queue.h"
#include "object/event.h"

namespace funkycl {

cl_int static 
clWaitForEvents(cl_uint             num_events,
                const cl_event *    event_list)
{
  if(num_events == 0) {
    DEBUG_STREAM("There are no events to be waited. ");
    return CL_SUCCESS;
  }

  std::vector<int> wait_event_ids(num_events);

  for(auto i=0; i<num_events; i++)
    wait_event_ids[i] = cl_to_funkycl(event_list[i])->get_id();

  /* event_id is not used for this request. The 1st argument is ignored by the backend. */
  funky_msg::event_info wait_info(0, num_events, &wait_event_ids[0]);

  /* cmdq_id is not used for this request. The 2nd argument is ignored by the backend. */
  funky_msg::request sync_req(funky_msg::SYNC, funky_msg::WAITEVENTS, 0, &wait_info);
  auto device = cl_to_funkycl(event_list[0])->get_context()->get_device();
  device->vfpga_send_request(sync_req);

  // wait for SYNC resonse
  auto res = device->vfpga_get_response();

  // TODO: set up timeout?
  while(res == NULL)
    res = device->vfpga_get_response();

  DEBUG_STREAM("vFPGA is synced.");

  return CL_SUCCESS;
}

} // funkycl


CL_API_ENTRY cl_int CL_API_CALL
clWaitForEvents(cl_uint             num_events,
                const cl_event *    event_list) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clWaitForEvents(num_events, event_list);
}

