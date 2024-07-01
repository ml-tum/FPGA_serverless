#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/platform.h"

#include <string>

namespace funkycl {

static cl_int
clGetPlatformInfo(cl_platform_id   platform,
                  cl_platform_info param_name,
                  size_t           param_value_size,
                  void *           param_value,
                  size_t *         param_value_size_ret)
{
  // const char* platform_name = "Funky";
  std::string platform_name("Funky");

  switch (param_name)
  {
    case CL_PLATFORM_NAME : 
      if(param_value)
      {
        if(param_value_size < platform_name.length())
          return CL_INVALID_VALUE;

        platform_name.copy((char *)param_value, param_value_size, 0);
      }

      if(param_value_size_ret)
        *param_value_size_ret = platform_name.length();

      break;

    default:
      return CL_INVALID_PLATFORM;
  }


  return CL_SUCCESS;
}

} // funkycl


CL_API_ENTRY cl_int CL_API_CALL
clGetPlatformInfo(cl_platform_id   platform,
                  cl_platform_info param_name,
                  size_t           param_value_size,
                  void *           param_value,
                  size_t *         param_value_size_ret) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clGetPlatformInfo
    (platform, param_name, param_value_size, param_value, param_value_size_ret);
}

