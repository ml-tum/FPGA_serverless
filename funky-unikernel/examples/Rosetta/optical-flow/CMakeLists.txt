cmake_minimum_required(VERSION 2.8.9)

# IncludeOS install location
if (NOT DEFINED ENV{INCLUDEOS_PREFIX})
  set(ENV{INCLUDEOS_PREFIX} /usr/local)
endif()

# macro which enables OpenCL APIs in Rosetta
# add_compile_definitions(OCL)
add_definitions(-DOCL)

include($ENV{INCLUDEOS_PREFIX}/includeos/pre.service.cmake)
project (rosetta)

set(SERVICE_NAME "3D rendering in rosetta")
set(BINARY       "funkycl-app")
set(CMAKE_BUILD_TYPE Debug)
set(HARNESS_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../harness)
set(IMAGE_LIB_DIR ${CMAKE_CURRENT_SOURCE_DIR}/imageLib)
set(VIVADO_HEADERS_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../vivado_headers)
set(FUNKY_UTILS_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../funky_utils)

# set(CMAKE_CXX_FLAGS "-O3 -Wall -Wextra")
set(CMAKE_CXX_FLAGS_DEBUG "-O0")
# set(MAX_MEM 128)

include_directories(${HARNESS_DIR})
include_directories(${FUNKY_UTILS_DIR})
include_directories(${VIVADO_HEADERS_DIR})

set(SOURCES 
  ${FUNKY_UTILS_DIR}/memdisk/diskio.cpp
  ${HARNESS_DIR}/CLWorld.cpp
  ${HARNESS_DIR}/CLKernel.cpp
  ${HARNESS_DIR}/CLMemObj.cpp
  ${IMAGE_LIB_DIR}/Convert.cpp  
  ${IMAGE_LIB_DIR}/flowIO.cpp  
  ${IMAGE_LIB_DIR}/ImageIO.cpp
  ${IMAGE_LIB_DIR}/Convolve.cpp  
  ${IMAGE_LIB_DIR}/Image.cpp   
  ${IMAGE_LIB_DIR}/RefCntMem.cpp
  utils.cpp
  check_result.cpp
  optical_flow_host.cpp)

if ("$ENV{PLATFORM}" STREQUAL "x86_solo5")
  set(DRIVERS 
    solo5fpga
    )
endif()

set(LIBRARIES
  libfunkycl.a
  )

# include service build script
include($ENV{INCLUDEOS_PREFIX}/includeos/post.service.cmake)

# mount a bitstream file in VFS by using memdisk
diskbuilder(../../../xclbin/u50/optical-flow)
