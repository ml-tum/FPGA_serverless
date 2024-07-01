#include "program.h"

namespace funkycl
{

  /** 
   * The constructor sends an init request to backend (ukvm) 
   *
   * OpenCL allows a context to have multiple program objects. 
   * However, the current version of FunkyCL supports that only a single program object is assigned to each device. 
   * It means a single program object contains all the kernels used by a guest application on the device. 
   *
   * */
program::
program(context* cntx, cl_uint num_devices, const cl_device_id* devices,
        const unsigned char** binaries, const size_t* lengths)
  : m_context(cntx)
{
  // TODO: check if the device (backend) is already initialized by another program.  
  for (cl_uint i=0; i < num_devices; i++) {
    auto device = funkycl::cl_to_funkycl(devices[i]);
    m_devices.push_back(device);

    /* 
     * Copy the bitstream file into memory. This is a little time-consuming (~50ms) but necessary 
     * because if the guest closes the file immediately after calling clCreateProgram(), 
     * we can no more find the bitstream file location. This means we can't do migration for the guest. 
     * */
    m_binaries.emplace(device, std::vector<unsigned char>{binaries[i], binaries[i] + lengths[i]});

    /* The device (vFPGA) is initialized only once unless it is freed. */
    if(!device->is_initialized()) {
      auto binary = m_binaries.find(device)->second;
      device->init_vfpga(binary);
    }

    // TODO: if the device is already initialized but this program context is instantiated with different bitstream, notify to the backend
    //      (for future extension, which allows a single guest app to manage multiple programs)
  }
}

program::
~program()
{
  DEBUG_STREAM("destroy program obj");

  /* notify the backend to release FPGA */
  // TODO: check if this iteration prevent retaining ownership. 
  //       The original code (xocl) uses boost::range(), but boost library is not linked to unikernel bin
  for (auto itr = device_iterator_type(m_devices.begin()); itr != device_iterator_type(m_devices.end()); itr++)
  {
    auto device = itr->get();
    if(device->is_initialized())
      device->free_vfpga();
  }
}

context* 
program::get_context()
{
  return m_context.get(); 
}

} // funkycl


