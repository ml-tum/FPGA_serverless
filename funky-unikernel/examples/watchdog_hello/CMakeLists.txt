cmake_minimum_required(VERSION 2.8.9)

# IncludeOS install location
if (NOT DEFINED ENV{INCLUDEOS_PREFIX})
  set(ENV{INCLUDEOS_PREFIX} /usr/local)
endif()
include($ENV{INCLUDEOS_PREFIX}/includeos/pre.service.cmake)
project (watchdog_hello)

# Human-readable name of your service
set(SERVICE_NAME "IncludeOS simple echo application, using watchdog")

# Name of your service binary
set(BINARY       "hello.bin")

# Source files to be linked with OS library parts to form bootable image
set(SOURCES
  hello.cpp # ...add more here
  )

# To add your own include paths:
# set(LOCAL_INCLUDES ".")

# DRIVERS / PLUGINS:

##if ("$ENV{PLATFORM}" STREQUAL "x86_solo5")
##  set(DRIVERS
##      solo5net
##    )
##else()
##endif()

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
##set(LIBRARIES libwatchdog.a)

# include service build script
include($ENV{INCLUDEOS_PREFIX}/includeos/post.service.cmake)
