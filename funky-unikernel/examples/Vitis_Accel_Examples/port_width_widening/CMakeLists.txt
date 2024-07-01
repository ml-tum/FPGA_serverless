cmake_minimum_required(VERSION 2.8.9)

# IncludeOS install location
if (NOT DEFINED ENV{INCLUDEOS_PREFIX})
  set(ENV{INCLUDEOS_PREFIX} /usr/local)
endif()

include($ENV{INCLUDEOS_PREFIX}/includeos/pre.service.cmake)
project (hello_xilinx)

# set(SERVICE_NAME "Service with no Service::start, only main")
set(SERVICE_NAME "hello world in Vitis_Accel_Examples")
set(BINARY       "funkycl-app")
set(CMAKE_BUILD_TYPE Debug)
set(FUNKY_UTILS_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../funky_utils)

# set(CMAKE_CXX_FLAGS "-O3 -Wall -Wextra")
set(CMAKE_CXX_FLAGS_DEBUG "-O0")
# set(MAX_MEM 128)

include_directories(${FUNKY_UTILS_DIR})

set(SOURCES 
  ${FUNKY_UTILS_DIR}/xcl2/xcl2.cpp
  ${FUNKY_UTILS_DIR}/memdisk/diskio.cpp
  host.cpp)

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
diskbuilder(../../../xclbin/u50/port_width_widening)
