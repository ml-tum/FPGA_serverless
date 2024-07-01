#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/device.h"
#include "object/cmd_queue.h"

namespace funkycl {

static cl_int 
clFinish(cl_command_queue command_queue)
{
  auto cmd_queue = cl_to_funkycl(command_queue);
  auto device = cmd_queue->get_device();

  funky_msg::request sync_req(funky_msg::SYNC, funky_msg::FINISH, cmd_queue->get_id(), (funky_msg::event_info *) nullptr);
  device->vfpga_send_request(sync_req);

  /* do a hypercall to wake up vfpga backend request handler */
  // TODO: Before doing the hypercall, it must be verified if vfpga worker thread exists. 
  // In case the worker thread exists, the guest (unikernel) just wait for the SYNC response from backend
  // device->vfpga_handle_requests();

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
clFinish(cl_command_queue command_queue) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clFinish(command_queue);
}

