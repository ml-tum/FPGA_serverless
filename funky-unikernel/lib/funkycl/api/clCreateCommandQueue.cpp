#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/cmd_queue.h"

namespace funkycl {

static cl_command_queue
clCreateCommandQueue(cl_context                  context,
                     cl_device_id                device,
                     cl_command_queue_properties properties,
                     cl_int *                    errcode_ret)
{
  auto command_queue =
    std::make_unique<funkycl::cmd_queue>(cl_to_funkycl(context), cl_to_funkycl(device), properties);

  if(errcode_ret)
    *errcode_ret = CL_SUCCESS;

  return command_queue.release();
}

} // funkycl


cl_command_queue
clCreateCommandQueue(cl_context                  context,
                     cl_device_id                device,
                     cl_command_queue_properties properties,
                     cl_int *                    errcode_ret)
{
  return funkycl::clCreateCommandQueue
    (context, device, properties, errcode_ret);
}


