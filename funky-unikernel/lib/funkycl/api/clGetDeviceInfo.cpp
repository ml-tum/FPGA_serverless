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

// Copyright 2016 Xilinx, Inc. All rights reserved.

#include <iostream>

#include "config.h"
#include <CL/opencl.h>
#include "object/object.h"
#include "object/platform.h"
#include "object/device.h"

#include <string>
#include <cstring>

namespace {

// TODO: it might not work for a specific class (e.g., std::string for which sizeof() cannot be used)
struct cl_param
{
  public:
    cl_param(void* value, size_t size, size_t* size_ret)
      : m_value(value), m_size(size), m_size_ret(size_ret)
    {}

    ~cl_param()
    {}

    void* m_value;
    size_t m_size;
    size_t* m_size_ret;
};

template <typename T>
cl_int update(cl_param &param, T value)
{
  if (param.m_size_ret)
    *(param.m_size_ret) = sizeof(T);

  if(param.m_value == nullptr)
    return CL_SUCCESS;

  if( (param.m_size < sizeof(T)) )
    return CL_INVALID_VALUE;

  // TODO: do a cast if m_value and value has a different type
  *(T*)(param.m_value) = value;

  return CL_SUCCESS;
}

template <>
cl_int update<const char*>(cl_param &param, const char* value)
{
  /* 
   * param_value_size need to be set before returning. 
   * param.m_value can be null while param.m_size_ret is valid (e.g., opencl-cpp wrapper) 
   */
  size_t str_size = strlen(value)+1;

  if (param.m_size_ret)
  {
    // memcpy(param.m_size_ret, &str_size, sizeof(str_size));
    *(param.m_size_ret) = str_size;
    DEBUG_STREAM("size_ret: " << std::dec << *(param.m_size_ret));
  }

  if(param.m_value == nullptr)
  {
    DEBUG_STREAM("success. (m_value is null)");
    return CL_SUCCESS;
  }

  if( param.m_size < str_size )
  {
    DEBUG_STREAM("Error. (m_value is too small)");
    return CL_INVALID_VALUE;
  }

  strncpy((char*)(param.m_value), value, str_size);
  DEBUG_STREAM("char: " << (char*) param.m_value);

  return CL_SUCCESS;
}

}

namespace funkycl {

static cl_int
clGetDeviceInfo(cl_device_id   device,
                  cl_platform_info param_name,
                  size_t           param_value_size,
                  void *           param_value,
                  size_t *         param_value_size_ret)
{
  auto f_device = cl_to_funkycl(device);

  cl_param param(param_value, param_value_size, param_value_size_ret);
  cl_int ret = CL_INVALID_VALUE;

  switch(param_name) {
  case CL_DEVICE_TYPE:
    // TODO: implement herefor 
    // buffer.as<cl_device_type>() = CL_DEVICE_TYPE_ACCELERATOR;
    ret = update<cl_device_type>(param, CL_DEVICE_TYPE_ACCELERATOR);
    break;
  case CL_DEVICE_VENDOR_ID:
    // buffer.as<cl_uint>() = 0;
    break;
  case CL_DEVICE_MAX_COMPUTE_UNITS:
    // buffer.as<cl_uint>() = xdevice->get_num_cus();
    break;
  case CL_DEVICE_MAX_WORK_ITEM_DIMENSIONS:
    // buffer.as<cl_uint>() = 3;
    break;
  case CL_DEVICE_MAX_WORK_ITEM_SIZES:
    // buffer.as<size_t>() = xocl::get_range(std::initializer_list<size_t>({maxuint,maxuint,maxuint}));
    break;
  case CL_DEVICE_MAX_WORK_GROUP_SIZE:
    // buffer.as<size_t>() = maxuint;
    break;
  case CL_DEVICE_PREFERRED_VECTOR_WIDTH_CHAR:
    // buffer.as<cl_uint>() = 1;
    break;
  case CL_DEVICE_PREFERRED_VECTOR_WIDTH_SHORT:
    // buffer.as<cl_uint>() = 1;
    break;
  case CL_DEVICE_PREFERRED_VECTOR_WIDTH_INT:
    // buffer.as<cl_uint>() = 1;
    break;
  case CL_DEVICE_PREFERRED_VECTOR_WIDTH_LONG:
    // buffer.as<cl_uint>() = 1;
    break;
  case CL_DEVICE_PREFERRED_VECTOR_WIDTH_FLOAT:
    // buffer.as<cl_uint>() = 1;
    break;
  case CL_DEVICE_PREFERRED_VECTOR_WIDTH_DOUBLE:
    // buffer.as<cl_uint>() = 0;
    break;
  case CL_DEVICE_PREFERRED_VECTOR_WIDTH_HALF:
    // buffer.as<cl_uint>() = 1;
    break;
  case CL_DEVICE_NATIVE_VECTOR_WIDTH_CHAR:
    // buffer.as<cl_uint>() = 1;
    break;
  case CL_DEVICE_NATIVE_VECTOR_WIDTH_SHORT:
    // buffer.as<cl_uint>() = 1;
    break;
  case CL_DEVICE_NATIVE_VECTOR_WIDTH_INT:
    // buffer.as<cl_uint>() = 1;
    break;
  case CL_DEVICE_NATIVE_VECTOR_WIDTH_LONG:
    // buffer.as<cl_uint>() = 1;
    break;
  case CL_DEVICE_NATIVE_VECTOR_WIDTH_FLOAT:
    // buffer.as<cl_uint>() = 1;
    break;
  case CL_DEVICE_NATIVE_VECTOR_WIDTH_DOUBLE:
    // buffer.as<cl_uint>() = 1;
    break;
  case CL_DEVICE_NATIVE_VECTOR_WIDTH_HALF:
    // buffer.as<cl_uint>() = 1;
    break;
  case CL_DEVICE_MAX_CLOCK_FREQUENCY:
    // buffer.as<cl_uint>() = xdevice->get_max_clock_frequency();
    break;
  case CL_DEVICE_ADDRESS_BITS:
    // buffer.as<cl_uint>() = 64;
    break;
  case CL_DEVICE_MAX_MEM_ALLOC_SIZE:
    // buffer.as<cl_ulong>() =
#ifdef __x86_64__
    //  4ULL *1024*1024*1024; // 4GB
#else
    //  128*1024*1024; //128 MB
#endif
    break;
  case CL_DEVICE_IMAGE_SUPPORT:
    // buffer.as<cl_bool>() = CL_TRUE;
    break;
  case CL_DEVICE_MAX_READ_IMAGE_ARGS:
    // buffer.as<cl_uint>() = 128;
    break;
  case CL_DEVICE_MAX_WRITE_IMAGE_ARGS:
    // buffer.as<cl_uint>() = 8;
    break;
  case CL_DEVICE_IMAGE2D_MAX_WIDTH:
    // buffer.as<size_t>() = 8192;
    break;
  case CL_DEVICE_IMAGE2D_MAX_HEIGHT:
    // buffer.as<size_t>() = 8192;
    break;
  case CL_DEVICE_IMAGE3D_MAX_WIDTH:
    // buffer.as<size_t>() = 2048;
    break;
  case CL_DEVICE_IMAGE3D_MAX_HEIGHT:
    // buffer.as<size_t>() = 2048;
    break;
  case CL_DEVICE_IMAGE3D_MAX_DEPTH:
    // buffer.as<size_t>() = 2048;
    break;
  case CL_DEVICE_IMAGE_MAX_BUFFER_SIZE:
    // buffer.as<size_t>() = 65536;
    break;
  case CL_DEVICE_IMAGE_MAX_ARRAY_SIZE:
    // buffer.as<size_t>() = 2048;
    break;
  case CL_DEVICE_MAX_SAMPLERS:
    // buffer.as<cl_uint>() = 0;
    break;
  case CL_DEVICE_MAX_PARAMETER_SIZE:
    // buffer.as<size_t>() = 2048;
    break;
  case CL_DEVICE_MEM_BASE_ADDR_ALIGN:
    // buffer.as<cl_uint>() = xocl(device)->get_alignment() << 3;  // in bits
    break;
  case CL_DEVICE_MIN_DATA_TYPE_ALIGN_SIZE:
    // buffer.as<cl_uint>() = 128;
    break;
  case CL_DEVICE_SINGLE_FP_CONFIG:
    // buffer.as<cl_device_fp_config>() = CL_FP_ROUND_TO_NEAREST | CL_FP_INF_NAN;
    break;
  case CL_DEVICE_DOUBLE_FP_CONFIG:
    // buffer.as<cl_device_fp_config>() = 0;
    break;
  case CL_DEVICE_GLOBAL_MEM_CACHE_TYPE:
    // buffer.as<cl_device_mem_cache_type>() = CL_NONE;
    break;
  case CL_DEVICE_GLOBAL_MEM_CACHELINE_SIZE:
    // buffer.as<cl_uint>() = 64;
    break;
  case CL_DEVICE_GLOBAL_MEM_CACHE_SIZE:
    // buffer.as<cl_ulong>() = 0;
    break;
  case CL_DEVICE_GLOBAL_MEM_SIZE:
    // buffer.as<cl_ulong>() = xdevice->get_xrt_device()->getDdrSize();
    break;
  case CL_DEVICE_MAX_CONSTANT_BUFFER_SIZE:
    // buffer.as<cl_ulong>() = 4*1024*1024;
    break;
  case CL_DEVICE_MAX_CONSTANT_ARGS:
    // buffer.as<cl_uint>() = 8;
    break;
  case CL_DEVICE_LOCAL_MEM_TYPE:
    // buffer.as<cl_device_local_mem_type>() = CL_LOCAL;
    break;
  case CL_DEVICE_LOCAL_MEM_SIZE:
    // buffer.as<cl_ulong>() = 16*1024;
    break;
  case CL_DEVICE_ERROR_CORRECTION_SUPPORT:
    // buffer.as<cl_bool>() = CL_TRUE;
    break;
  case CL_DEVICE_HOST_UNIFIED_MEMORY:
    // buffer.as<cl_bool>() = CL_TRUE;
    break;
  case CL_DEVICE_PROFILING_TIMER_RESOLUTION:
    // buffer.as<size_t>() = 1;
    break;
  case CL_DEVICE_ENDIAN_LITTLE:
    // buffer.as<cl_bool>() = CL_TRUE;
    break;
  case CL_DEVICE_AVAILABLE:
    // buffer.as<cl_bool>() = xdevice->is_available();
    break;
  case CL_DEVICE_COMPILER_AVAILABLE:
    // buffer.as<cl_bool>() = CL_FALSE;
    break;
  case CL_DEVICE_LINKER_AVAILABLE:
    // buffer.as<cl_bool>() = CL_TRUE;
    break;
  case CL_DEVICE_EXECUTION_CAPABILITIES:
    // buffer.as<cl_device_exec_capabilities>() = CL_EXEC_KERNEL;
    break;
  case CL_DEVICE_QUEUE_PROPERTIES:
    // buffer.as<cl_command_queue_properties>() =
    //  (
    //   CL_QUEUE_OUT_OF_ORDER_EXEC_MODE_ENABLE
    //   | CL_QUEUE_PROFILING_ENABLE
    // );
    break;
  case CL_DEVICE_BUILT_IN_KERNELS:
    // buffer.as<char>() = "";
    break;
  case CL_DEVICE_PLATFORM:
    // buffer.as<cl_platform_id>() = xdevice->get_platform();
    break;
  case CL_DEVICE_NAME:
    ret = update<const char*>(param, "xilinx_u50_gen3x16_xdma_201920_3\0");
    // ret = update<const char*>(param, "xilinx_u50_gen3x16_xdma_201920_3");
    // buffer.as<char>() = xdevice->get_name();
    break;
  case CL_DEVICE_VENDOR:
    // buffer.as<char>() = "Xilinx";
    break;
  case CL_DRIVER_VERSION:
    // buffer.as<char>() = "1.0";
    break;
  case CL_DEVICE_PROFILE:
    // buffer.as<char>() = "EMBEDDED_PROFILE";
    break;
  case CL_DEVICE_VERSION:
    // buffer.as<char>() = "OpenCL 1.0";
    break;
  case CL_DEVICE_OPENCL_C_VERSION:
    // buffer.as<char>() = "OpenCL C 1.0";
    break;
  case CL_DEVICE_EXTENSIONS:
    // buffer.as<char>() = "";
    //12: "cl_khr_global_int32_base_atomics cl_khr_global_int32_extended_atomics cl_khr_local_int32_base_atomics cl_khr_local_int32_extended_atomics cl_khr_byte_addressable_store";
    break;
  case CL_DEVICE_PRINTF_BUFFER_SIZE:
    // buffer.as<size_t>() = 0;
    break;
  case CL_DEVICE_PREFERRED_INTEROP_USER_SYNC:
    // buffer.as<cl_bool>() = CL_TRUE;
    break;
  case CL_DEVICE_PARENT_DEVICE:
    // buffer.as<cl_device_id>() = xdevice->get_parent_device();
    break;
  case CL_DEVICE_PARTITION_MAX_SUB_DEVICES:
    // buffer.as<cl_uint>() = xdevice->get_num_cus();
    break;
  case CL_DEVICE_PARTITION_PROPERTIES:
    // buffer.as<cl_device_partition_property>() =
      // xocl::get_range(std::initializer_list<cl_device_partition_property>({0,0,0,0}));
    break;
  case CL_DEVICE_PARTITION_AFFINITY_DOMAIN:
    // buffer.as<cl_device_affinity_domain>() = 0;
    break;
  case CL_DEVICE_PARTITION_TYPE:
    // buffer.as<cl_device_partition_property>() =
      // xocl::get_range(std::initializer_list<cl_device_partition_property>({0,0,0,0}));
    break;
  case CL_DEVICE_REFERENCE_COUNT:
    // buffer.as<cl_uint>() = xdevice->count();
    break;
  //depricated in OpenCL 1.2
  case CL_DEVICE_MAX_PIPE_ARGS:
    // buffer.as<cl_uint>() = 16;
    break;
  case CL_DEVICE_PIPE_MAX_ACTIVE_RESERVATIONS:
    // buffer.as<cl_uint>() = 1;
    break;
  case CL_DEVICE_PIPE_MAX_PACKET_SIZE:
    // buffer.as<cl_uint>() = 1024;
    break;
  case CL_DEVICE_SVM_CAPABILITIES:
    // buffer.as<cl_device_svm_capabilities>() = CL_DEVICE_SVM_COARSE_GRAIN_BUFFER;
    break;
  // NOTE: the following macros are specific to Xilinx XRT?
  // case CL_DEVICE_PCIE_BDF:
  //   // buffer.as<char>() = xdevice->get_bdf();
  //   break;
  // case CL_DEVICE_HANDLE:
  //   // buffer.as<void*>() = xdevice->get_handle();
  //   break;
  // case CL_DEVICE_NODMA:
  //   // buffer.as<cl_bool>() = xdevice->is_nodma();
  //   break;
  default:
    // TODO: use debugprint function of IncludeOS
    std::cout << "clGetDeviceInfo: invalid param_name" << std::endl;
    ret = CL_INVALID_VALUE;
    break;
  }

  return ret;
}

} // funkycl

CL_API_ENTRY cl_int CL_API_CALL
clGetDeviceInfo(cl_device_id    device,
                cl_device_info  param_name,
                size_t          param_value_size,
                void *          param_value,
                size_t *        param_value_size_ret) CL_API_SUFFIX__VERSION_1_0
{
  return funkycl::clGetDeviceInfo
    (device, param_name, param_value_size, param_value, param_value_size_ret);
}



