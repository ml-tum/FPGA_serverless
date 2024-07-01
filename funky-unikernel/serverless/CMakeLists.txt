cmake_minimum_required(VERSION 2.8.9)

# IncludeOS install location
#if (NOT DEFINED ENV{INCLUDEOS_PREFIX})
#  set(ENV{INCLUDEOS_PREFIX} /usr/local)
#endif()
include($ENV{INCLUDEOS_PREFIX}/includeos/pre.service.cmake)
project (serverless)

# Human-readable name of your service
set(SERVICE_NAME "IncludeOS / Serverless FPGA / $ENV{CPP_FILE}")

# Name of your service binary
set(BINARY       "serverless.bin")

# Source files to be linked with OS library parts to form bootable image
set(SOURCES
#  sha3-fpga.cpp
  $ENV{CPP_FILE}
  src/watchdog.cpp
  src/microtar.c
  )

# To add your own include paths:
# set(LOCAL_INCLUDES ".")

# DRIVERS / PLUGINS:
if ("$ENV{PLATFORM}" STREQUAL "x86_solo5")
  set(DRIVERS
      solo5net
    )
else()
  set(DRIVERS
      virtionet     # Virtio networking
      vmxnet3
      boot_logger   # Display boot information

    # Use "boot --drivers ." to see other drivers
    # virtioblk # Virtio block device
    # ... Others from src/drivers
    )
endif()

set(PLUGINS
  )

# Library to be linked into the service image
#set(LIBRARIES libwatchdog.a)

# include service build script
include($ENV{INCLUDEOS_PREFIX}/includeos/post.service.cmake)

# What is private and public?
target_compile_options(service PRIVATE -Wno-deprecated-copy -Wno-address-of-packed-member)
#target_compile_options(service PUBLIC -Wno-deprecated-copy)

#SET(CMAKE_FIND_LIBRARY_SUFFIXES ".a")
#find_package(JPEG)
#target_link_libraries(service JPEG::JPEG)

#add_library(service libspng_static.a)

#set(LIBRARIES libspng_static.a)
#target_link_libraries(service PRIVATE ./libspng_static.a)

#target_link_libraries(service m)

#SET(CMAKE_FIND_LIBRARY_SUFFIXES ".a")
##set(ZLIB_USE_STATIC_LIBS ON)
#find_package(ZLIB)
#target_link_libraries(service ZLIB::ZLIB)
#find_package(PNG)
#include_directories(${PNG_INCLUDE_DIR})
##target_link_libraries(service ${PNG_LIBRARY})
#target_link_libraries(service PNG::PNG)