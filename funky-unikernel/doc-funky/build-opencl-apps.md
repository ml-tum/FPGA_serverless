## Prerequisites

- install libraries required for compiling IncludeOS (See [build-without-scripts.md](./build-without-scripts.md))
- install XRT 2020.2 or higher (See [the Xilinx website](https://xilinx.github.io/XRT/master/html/install.html))

## 1. Build Funky unikernel

The compiling flow is almost the same as written in [build-without-scripts.md](./build-without-scripts.md), but you have to set a path to XRT library in advance. If XRT is already installed in your machine, you can do this by `source /opt/xilinx/xrt/setup.sh`.

```
# Set up the path
export INCLUDEOS_PREFIX=~/funkyos/
export CC="clang"
export CXX="clang++"
source /opt/xilinx/xrt/setup.sh

# Prepare for build
git clone git@github.com:TUM-DSE/funky-unikernel.git
cd funky-unikernel 
mkdir ~/funkyos 
mkdir build && cd build 

# Build and install
cmake .. -DCMAKE_INSTALL_PREFIX=${INCLUDEOS_PREFIX} 
make PrecompiledLibraries
make -j `grep processor /proc/cpuinfo | wc -l`
make install 
```

## 2. Build an OpenCL application

[hello_xilinx](../examples/hello_xilinx) is a base OpenCL application that configures a vector-add accelerator on FPGA and offloads the computation of A+B (A, B are 4k vector data of integer). 
This app is ported from [hello_world in Vitis_Accel_Examples](https://github.com/Xilinx/Vitis_Accel_Examples/tree/master/hello_world).

Here is a cmake file of [hello_xilinx](../examples/hello_xilinx). solo5fpga is a driver used to send/receive FPGA control requests between the unikernel and backend monitor (ukvm). libfunkycl.a is a 'virtual' OpenCL library named FunkyCL, which abstracts communications between unikernel/ukvm. FunkyCL allows an app to use OpenCL C/C++ APIs without modifying codes, as if the app was running on a native environment. 

```
cmake_minimum_required(VERSION 2.8.9)

# IncludeOS install location
if (NOT DEFINED ENV{INCLUDEOS_PREFIX})
  set(ENV{INCLUDEOS_PREFIX} /usr/local)
endif()

include($ENV{INCLUDEOS_PREFIX}/includeos/pre.service.cmake)
project (hello_xilinx)

set(SERVICE_NAME "hello world in Vitis Accel Examples")
set(BINARY       "funkycl-app")
set(CMAKE_BUILD_TYPE Debug)
# set(MAX_MEM 128)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/xcl2)

set(SOURCES
  xcl2/xcl2.hpp
  xcl2/xcl2.cpp
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
diskbuilder(disk)
```

For compiling this app, you can use a script named [build.sh](../funky-scripts/examples/build.sh).
```
./build.sh -h # show help
./build.sh build
```

The result will be a `funkycl-app` elf 64-bit executable in build/.


## 3. Deploy the unikernel 

For deploying the unikernel app, you can use a script named [execute.sh](../funky-scripts/examples/build.sh). Its usage is displayed by `./execute.sh -h`: 

```
$ ./execute.sh -h

Usage:
  execute.sh [<options>]

Options:
  -h                    print help

  -g                    run the unikernel with gdb

  -b <build_dir>        set path to dir including binary
                        (default: build/)

  -u <ukvm-bin>         set path to ukvm-bin
                        (default: /home/atsushi/funkyos//includeos/x86_64/lib/ukvm-bin)

  -t <network device>   set tap device
                        (default: tap100)

  -a <arguments...>     set arguments for the app
```

If you have not set up the tap device, execute the following commands:

```
### create a tap device named 'tap100'
sudo ip tuntap add tap100 mode tap user $USER
sudo ip link set dev tap100 up
sudo ip addr add 10.0.0.1/24 dev tap100

### you can also remove the tap device
sudo ip tuntap del tap100 mode tap
```

Now we are ready to deploy a unikernel: 
```
./execute.sh -b build
```

