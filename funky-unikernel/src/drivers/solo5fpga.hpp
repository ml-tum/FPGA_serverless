// This file is a part of the IncludeOS unikernel - www.includeos.org
//
// Copyright 2015 Oslo and Akershus University College of Applied Sciences
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
#ifndef SOLO5_FPGA_HPP
#define SOLO5_FPGA_HPP

#include <common>
#include <hw/fpga.hpp>
// #include <hw/block_device.hpp>
// #include <hw/pci_device.hpp>
// #include <virtio/virtio.hpp>
#include <deque>

class Solo5FPGA : public hw::FPGA
{
public:

  static std::unique_ptr<FPGA> new_instance()
  {
    // INFO("Solo5FPGA", "Creating new FPGA instance...");
    return std::make_unique<Solo5FPGA>();
  }

  std::string device_name() const override { // stays
    return "vfpga" + std::to_string(id());
  }

  /** Human readable name. */
  const char* driver_name() const noexcept override { // stays
    return "Solo5FPGA";
  }

  int init(void*, size_t, void*, size_t, void*, size_t) override; // stays

  int handle_requests(void) override; // stays

  int free() override; // stays

  void deactivate() override; // stays

  /** Constructor. */
  Solo5FPGA();

private:
};

#endif //< SOLO5_FPGA_HPP
