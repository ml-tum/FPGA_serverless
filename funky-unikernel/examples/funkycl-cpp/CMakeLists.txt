cmake_minimum_required(VERSION 2.8.9)

# IncludeOS install location
if (NOT DEFINED ENV{INCLUDEOS_PREFIX})
  set(ENV{INCLUDEOS_PREFIX} /usr/local)
endif()

include($ENV{INCLUDEOS_PREFIX}/includeos/pre.service.cmake)
project (funkycl)

# set(SERVICE_NAME "Service with no Service::start, only main")
set(SERVICE_NAME "Test for Funky OpenCL C++ APIs")
set(BINARY       "funkycl-cpp")
# set(MAX_MEM 128)

set(FUNKY_UTILS_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../funky_utils)
include_directories(${FUNKY_UTILS_DIR})

set(SOURCES 
  ${FUNKY_UTILS_DIR}/xcl2/xcl2.cpp
  main.cpp)

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
