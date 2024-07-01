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
clGetEventProfilingInfo(cl_event            event,
                        cl_profiling_info   param_name,
                        size_t              param_value_size,
                        void *              param_value,
                        size_t *            param_value_size_ret)
{

  if(param_value_size < sizeof(cl_ulong))
    return CL_INVALID_VALUE;

  /* set param_value and param_name in event_info */
  auto f_event = cl_to_funkycl(event);
  funky_msg::event_info profiling_info(f_event->get_id(), 0, nullptr, param_name, param_value);
  DEBUG_STREAM("event id: " << f_event->get_id() << ", param name: " << std::hex << param_name << ", param ptr: " << param_value);

  // f_event->set_param_in_eventinfo(param_name, param_value);

  /* send a "SYNC" request to backend */
  auto context = f_event->get_context();
  auto device = context->get_device();

  funky_msg::request profiling_req(funky_msg::SYNC, funky_msg::PROFILE, 0, &profiling_info);
  device->vfpga_send_request(profiling_req);

  // wait for SYNC resonse
  auto res = device->vfpga_get_response();

  // TODO: set up timeout?
  while(res == NULL)
    res = device->vfpga_get_response();

  return CL_SUCCESS;
}

} // funkycl


CL_API_ENTRY cl_int CL_API_CALL
clGetEventProfilingInfo(cl_event            event,
                        cl_profiling_info   param_name,
                        size_t              param_value_size,
                        void *              param_value,
                        size_t *            param_value_size_ret) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clGetEventProfilingInfo
    (event, param_name, param_value_size, param_value, param_value_size_ret);
}

