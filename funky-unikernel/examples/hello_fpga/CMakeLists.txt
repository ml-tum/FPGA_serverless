cmake_minimum_required(VERSION 2.8.9)

# IncludeOS install location
if (NOT DEFINED ENV{INCLUDEOS_PREFIX})
  set(ENV{INCLUDEOS_PREFIX} /usr/local)
endif()

include($ENV{INCLUDEOS_PREFIX}/includeos/pre.service.cmake)
project (hello_fpga)

# set(SERVICE_NAME "Service with no Service::start, only main")
set(SERVICE_NAME "Test for Funky FPGA")
set(BINARY       "hello_fpga")
set(MAX_MEM 128)

option(NORMAL "" ON)


if (NORMAL)
  set(SOURCES service.cpp)
else()
  set(SOURCES main_no_params.cpp)
endif()

if ("$ENV{PLATFORM}" STREQUAL "x86_solo5")
  set(DRIVERS 
    solo5fpga
    )
endif()

# include service build script
include($ENV{INCLUDEOS_PREFIX}/includeos/post.service.cmake)
