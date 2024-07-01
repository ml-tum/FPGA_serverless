#include "platform.h"
#include "device.h"

namespace funkycl
{


platform::platform() : m_device(std::make_unique<funkycl::device>(this))
{}

platform::~platform()
{
  // TODO: release cl_device objects
}

std::shared_ptr<platform>
platform::get_shared_platform()
{
  static auto global_platform = std::make_shared<platform>();
  return global_platform;
}

device* 
platform::get_device()
{
  return m_device.get();
}


platform* get_global_platform()
{
  return platform::get_shared_platform().get();
}

} // funkycl

