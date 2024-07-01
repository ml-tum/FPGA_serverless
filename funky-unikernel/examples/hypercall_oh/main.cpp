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

#include <timers>

#include <hw/fpga.hpp>

int main(int argc, char** argv)
{
  std::vector<uint8_t> dummy_bs = {0xde, 0xad, 0xbe, 0xef};

  auto& fpga = hw::Devices::fpga(0);

  printf("FPGA is obtained.\n");

  printf("device name: %s \n", fpga.device_name().c_str());
  printf("driver name: %s \n", fpga.driver_name());

  std::cout << "hypercall oh [ns]: " << std::endl;

#define REPEAT_NUM 100
  auto sum = std::chrono::nanoseconds(0).count();

  auto i=0;
  for (; i < REPEAT_NUM; i++)
  {
    auto st = std::chrono::high_resolution_clock::now(); // Results in a nanosecond?
    fpga.init(dummy_bs.data(), dummy_bs.size());
    auto en = std::chrono::high_resolution_clock::now(); // Results in a nanosecond?

    auto oh = std::chrono::duration_cast<std::chrono::nanoseconds>(en - st).count();
    sum += oh;
    std::cout << oh << ", ";
  }
  std::cout << std::endl << (sum/REPEAT_NUM) << ", (avg.)" << std::endl;

  sum = 0;
  std::cout << "measurement only [ns]: " << std::endl;
  for (i=0; i < REPEAT_NUM; i++)
  {
    auto st = std::chrono::high_resolution_clock::now(); // Results in a nanosecond?
    auto en = std::chrono::high_resolution_clock::now(); // Results in a nanosecond?

    auto oh = std::chrono::duration_cast<std::chrono::nanoseconds>(en - st).count();
    sum += oh;
    std::cout << oh << ", ";
  }
  std::cout << std::endl << (sum/REPEAT_NUM) << ", (avg.)" << std::endl;

  return 0;
}
