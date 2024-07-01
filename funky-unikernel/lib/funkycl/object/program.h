#ifndef __PROGRAM_H
#define __PROGRAM_H

#include <memory>
#include <vector>
#include <map>

#include "object.h"
#include "refcount.h"
#include "platform.h"
#include "device.h"
#include "context.h"

namespace funkycl {
#define FUNKY_VFPGA_ID 1

class program : public _cl_program, public refcount
{
public:
  program(context* cntx, cl_uint num_devices, const cl_device_id* devices,
        const unsigned char** binaries, const size_t* lengths);
  ~program();

  using device_vector_type = std::vector<ptr<device>>;
  using device_iterator_type = ptr_iterator<device_vector_type::iterator>;

  context* get_context();

private:
  // context* m_context;
  ptr<context> m_context;
  // std::vector<device*> m_devices;
  std::vector<ptr<device>> m_devices;

  std::map<const device*,std::vector<unsigned char>> m_binaries; // multiple binaries can be loaded
  std::map<const device*,std::string> m_options;

  // TODO: implement clCreateProgramWithSource()
  // std::string m_source;
};

} // namespace funkycl

#endif // __PROGRAM_H

