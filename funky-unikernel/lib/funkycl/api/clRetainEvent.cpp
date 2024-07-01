#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/event.h"

namespace funkycl {

static cl_int
clRetainEvent(cl_event event)
{
  DEBUG_STREAM("Retain event [" << cl_to_funkycl(event)->get_id() << "]: refcount=" << cl_to_funkycl(event)->count()+1);

  cl_to_funkycl(event)->retain();
  return CL_SUCCESS;
}

} // funkycl

CL_API_ENTRY cl_int CL_API_CALL
clRetainEvent(cl_event    event) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clRetainEvent(event);
}

