/**
 * Copyright (C) 2016-2017 Xilinx, Inc
 *
 * Licensed under the Apache License, Version 2.0 (the "License"). You may
 * not use this file except in compliance with the License. A copy of the
 * License is located at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

// Copyright 2017 Xilinx, Inc. All rights reserved.

#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/platform.h"

#include <iostream>

namespace {
static cl_device_type
getDeviceType(cl_device_id device)
{
  cl_device_type type = CL_DEVICE_TYPE_DEFAULT;
  clGetDeviceInfo(device, CL_DEVICE_TYPE, sizeof(cl_device_type), &type, nullptr);
  return type;
}
} // namespace

namespace funkycl {
static cl_int 
clGetDeviceIDs(cl_platform_id   platform,
               cl_device_type   device_type,
               cl_uint          num_entries,
               cl_device_id *   devices,
               cl_uint *        num_devices)
{
  if (!platform)
    platform = get_global_platform();

  auto f_platform = cl_to_funkycl(platform);

  // TODO: currently, Funky supports only one device (vfpga)
  //       This will be replaced by get_device_range()
  auto device = f_platform->get_device();

  cl_uint num_devices_cnt=0;

  switch(device_type)
  {
    case CL_DEVICE_TYPE_DEFAULT:
    case CL_DEVICE_TYPE_ALL:
      if (getDeviceType(device)!=CL_DEVICE_TYPE_CUSTOM) {
        if(num_entries > 0 && devices) {
          devices[0] = device;
        }
        num_devices_cnt++;
      }
      break;
    case CL_DEVICE_TYPE_CPU:
    case CL_DEVICE_TYPE_GPU:
    case CL_DEVICE_TYPE_ACCELERATOR:
      if(getDeviceType(device)==device_type) {
        if(num_entries >= 0 && devices) {
          devices[0] = device;
        }
        num_devices_cnt++;
      }
      break;
  }

  *num_devices = num_devices_cnt;

  return CL_SUCCESS;
}

} // funkycl

/* Device APIs */
CL_API_ENTRY cl_int CL_API_CALL
clGetDeviceIDs(cl_platform_id   platform,
               cl_device_type   device_type,
               cl_uint          num_entries,
               cl_device_id *   devices,
               cl_uint *        num_devices) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clGetDeviceIDs(platform, device_type, num_entries, devices, num_devices);
}

