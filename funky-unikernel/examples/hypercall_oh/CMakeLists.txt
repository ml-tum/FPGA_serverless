cmake_minimum_required(VERSION 2.8.9)

# IncludeOS install location
if (NOT DEFINED ENV{INCLUDEOS_PREFIX})
  set(ENV{INCLUDEOS_PREFIX} /usr/local)
endif()

include($ENV{INCLUDEOS_PREFIX}/includeos/pre.service.cmake)
project (hypercall_oh)

# set(SERVICE_NAME "Service with no Service::start, only main")
set(SERVICE_NAME "measure hypercall overhead")
set(BINARY       "hypercall_oh")
# set(MAX_MEM 128)

set(ENV{PLATFORM} x86_solo5)

set(SOURCES main.cpp)

if ("$ENV{PLATFORM}" STREQUAL "x86_solo5")
  set(DRIVERS 
    solo5fpga
    )
endif()

# set(LIBRARIES
#   libfunkycl_lib.a
#   )

# include service build script
include($ENV{INCLUDEOS_PREFIX}/includeos/post.service.cmake)
