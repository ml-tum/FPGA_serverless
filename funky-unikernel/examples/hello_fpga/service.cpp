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

#include <os>
#include <sstream>
#include <cstdio>
#include <string>
#include <cassert>

#include <vector>

#include <hw/fpga.hpp>

int main(int argc, char** argv)
{
  std::cout <<  "test" << std::endl;
  printf("Argc: %d\n", argc);

  for (int i = 0; i < argc; i++)
    printf("Arg %i: %s\n", i, argv[i]);

  std::vector<uint8_t> dummy_bs = {0xde, 0xad, 0xbe, 0xef};

  auto& fpga = hw::Devices::fpga(0);

  printf("FPGA is obtained.\n");

  // printf("FPGA is obtained.\n");

  printf("device name: %s \n", fpga.device_name().c_str());
  printf("driver name: %s \n", fpga.driver_name());

  // TODO: develop fpga.info() and replace here 
  // fpga.init(dummy_bs.data(), dummy_bs.size());

  // We want to veirify this "exit status" on the back-end
  return 200;
}
