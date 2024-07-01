#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/event.h"

namespace funkycl {

static cl_int
clReleaseEvent(cl_event event)
{
  DEBUG_STREAM("Release event [" << cl_to_funkycl(event)->get_id() << "]: refcount=" << cl_to_funkycl(event)->count()-1);

  if (cl_to_funkycl(event)->release())
  {
    DEBUG_STREAM("destroy event [" << cl_to_funkycl(event)->get_id() << "]!");
    delete cl_to_funkycl(event);
  }
  
  // if(event)
  //   delete cl_to_funkycl(event);
  // if (cl_to_funkycl(kernel)->release()) // release() cannot be called?

  return CL_SUCCESS;
}

} // funkycl

CL_API_ENTRY cl_int CL_API_CALL
clReleaseEvent(cl_event event) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clReleaseEvent(event);
}



