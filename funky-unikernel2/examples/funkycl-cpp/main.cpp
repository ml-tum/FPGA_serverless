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

#include "xcl2/xcl2.hpp"

// #define CL_TARGET_OPENCL_VERSION 120
// #include <hw/fpga.hpp>
// #include <CL/opencl.h>

int main()
{
  cl_int status;

  // Tutorial: Simple start with OpenCL and C++
  // http://simpleopencl.blogspot.com/2013/06/tutorial-simple-start-with-opencl-and-c.html
  
  //get all platforms (drivers)
  std::vector<cl::Platform> all_platforms;
  cl::Platform::get(&all_platforms);
  if(all_platforms.size()==0){
    std::cout<<" No platforms found. Check OpenCL installation!\n";
    exit(1);
  }
  cl::Platform default_platform=all_platforms[0];
  // FIXME: platform.getInfo() must return "Funky" but returns "Funk" now
  std::cout << "Using platform: "<<default_platform.getInfo<CL_PLATFORM_NAME>()<<"\n";
  
  return 0;
}
