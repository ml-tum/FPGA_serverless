// This file is a part of the IncludeOS unikernel - www.includeos.org
//
// Copyright 2015-2017 Oslo and Akershus University College of Applied Sciences
// and Alfred Bratterud
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once
#ifndef HW_FPGA_HPP
#define HW_FPGA_HPP

#include <cstdint>
#include <delegate>
#include <memory>
#include <pmr>
#include <vector>

namespace hw {

/**
 * This class is an abstract interface for FPGA devices
 */
class FPGA {
public:
  // using buffer_t      = os::mem::buf_ptr;
  // using on_read_func  = delegate<void(buffer_t)>;
  // using on_write_func = delegate<void(bool error)>;

  /**
   * Method to get the type of device
   *
   * @return The type of device as a C-String
   */
  static const char* device_type() noexcept
  { return "FPGA device"; }

  /**
   * Method to get the name of the device
   *
   * @return The name of the device as a std::string
   */
  virtual std::string device_name() const = 0;

  /**
   * Method to get the device's identifier
   *
   * @return The device's identifier
   */
  int id() const noexcept
  { return id_; }

  /**
   * Get the human-readable name of this device's controller
   *
   * @return The human-readable name of this device's controller
   */
  virtual const char* driver_name() const noexcept = 0;

  /**
   * obtain & initialize the FPGA region 
   *
   * @param bs
   *   A pointer to bitstream data 
   *
   * @param bs_len
   *   Byte size of bitstream
   *
   * @return 0 (success) or -1 (failed) 
   */
  virtual int init(void* bs, size_t bs_len, void* wr_queue, size_t wr_len, 
      void* rd_queue, size_t rd_len) = 0;

  /**
   * wakeup vfpga request handler (in backend)
   *
   * @return the number of retired requests
   */
  virtual int handle_requests(void) = 0;

  /**
   * release vFPGA (in backend)
   *
   * @return 0 (success) or -1 (failed) 
   */
  virtual int free(void) = 0;

  /**
   * Method to deactivate the block device
   */
  virtual void deactivate() = 0;

  virtual ~FPGA() noexcept = default;
protected:
  FPGA() noexcept
  {
    static int counter = 0;
    id_ = counter++;
  }
private:
  int id_;
}; //< class FPGA

} //< namespace hw

#endif //< HW_FPGA_HPP
