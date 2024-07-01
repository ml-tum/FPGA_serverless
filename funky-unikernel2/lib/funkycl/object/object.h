#ifndef __OBJECT_H
#define __OBJECT_H

#include "config.h"
#include <CL/cl.h>

/**
 * object.h - define OpenCL/FunkyCL objects 
 *
 * OpenCL objects (_cl_***) and their pointer objects are defined in CL/cl.h,
 * but no actual implementation.
 * i.e., typedef struct _cl_platform_id *    cl_platform_id;
 *
 * Funky CL objects (funkycl::***) are their implementation specific to Funky platform,
 * which override original OpenCL objects. 
 * 
 * A static downcast is used to access Funky CL objects with OpenCL pointer objects.
 *
 * Some functions refer to Xilinx XRT implementation (TODO: check an OSS license? Apache 2.0?)
 */

namespace funkycl {

class platform;
class device;
class context;
class cmd_queue;
class memory;
class program;
class kernel;
class event;
class sampler;

template  <typename FUNKY_OBJ, typename CL_OBJ>
class cl_object_base
{
  public:
    typedef FUNKY_OBJ funky_obj_type;
    typedef CL_OBJ cl_obj_type;
};

namespace detail {

template <typename CLTYPE>
struct cl_object_traits;

template <typename CLTYPE>
struct cl_object_traits<CLTYPE*>
{
  using funky_obj_type = typename CLTYPE::funky_obj_type;

  static funky_obj_type*
  get_funky_obj(CLTYPE* cl)
  {
    return static_cast<funky_obj_type*>(cl);
  }
};

}

template <typename CLTYPE>
typename detail::cl_object_traits<CLTYPE>::funky_obj_type*
cl_to_funkycl(CLTYPE c)
{
  return detail::cl_object_traits<CLTYPE>::get_funky_obj(c);
}

// template <typename CL_OBJ>
// typename CL_OBJ::funky_obj_type* cl_to_funkycl(CL_OBJ* cl_obj)
// {
//   return static_cast<typename CL_OBJ::cl_obj_type*>(cl_obj);
// }

}  // funkycl


struct _cl_platform_id  : public funkycl::cl_object_base<funkycl::platform, _cl_platform_id> {};
struct _cl_device_id    : public funkycl::cl_object_base<funkycl::device, _cl_device_id> {};
struct _cl_context      : public funkycl::cl_object_base<funkycl::context, _cl_context> {};
struct _cl_command_queue: public funkycl::cl_object_base<funkycl::cmd_queue, _cl_command_queue> {};
struct _cl_mem          : public funkycl::cl_object_base<funkycl::memory, _cl_mem> {};
struct _cl_program      : public funkycl::cl_object_base<funkycl::program, _cl_program> {};
struct _cl_kernel       : public funkycl::cl_object_base<funkycl::kernel, _cl_kernel> {};
struct _cl_event        : public funkycl::cl_object_base<funkycl::event, _cl_event> {};
struct _cl_sampler      : public funkycl::cl_object_base<funkycl::sampler, _cl_sampler> {};


#endif // __OBJECT_H
