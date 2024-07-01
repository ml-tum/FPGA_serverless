## Build and use IncludeOS unikernels

IncludeOS provides a lot of scripts which can set up the environment to build IncludeOS unikernels. The problem with these scripts is that they are based on python and make every script to work is not that easy. Most of the dependencies which can be found in pip require python3, but some of the provided scripts do not work with python3 (syntax errors). Even if specifying the package version, when using the `boot` command we might run into some errors again. It seems much easier if we just take a closer look into the scripts and try to build IncludeOS the same way. 

## IncludeOS build system

Unikernels are static binaries which are usually built by linking independent libraries together. IncludeOS follows the same paradigm. Looking at IncludeOS code we can see 4 directories with libraries:
1. OS Components and standard libraries
2. Drivers
3. Plugins
4. Platform

When we link the application we have to specify which drivers, platform and plugins our unikernel needs. On the other hand only the standard libraries which are needed from the application will be linked in the final binary.

## Building IncludeOS without install.sh

IncludeOS provides`install.sh` helper script which can do all the magic for us. On the other hand we can do all the essential things manually without using any scripts. One of the reasons to do that is to have a better understanding of the build system and to avoid dealing with python. 

At first we need to make sure that the following packages have been installed.

- curl
- make
- cmake
- nasm
- jq
- gcc
- g++-multilib

IncludeOS is using cmake for the build configuration. The available options are:
```
// Architecture (default)
ARCH:STRING=x86_64

// Local path of bundle with pre-compile libraries
BUNDLE_LOC:STRING=

// Path to a program.
CMAKE_AR:FILEPATH=/usr/bin/ar

// Path to a program.
CMAKE_ASM_NASM_COMPILER:FILEPATH=/usr/bin/nasm

// Flags used by the assembler during all build types.
CMAKE_ASM_NASM_FLAGS:STRING=

// Flags used by the assembler during debug builds.
CMAKE_ASM_NASM_FLAGS_DEBUG:STRING=

// Flags used by the assembler during release minsize builds.
CMAKE_ASM_NASM_FLAGS_MINSIZEREL:STRING=

// Flags used by the assembler during release builds.
CMAKE_ASM_NASM_FLAGS_RELEASE:STRING=

// Flags used by the assembler during Release with Debug Info builds.
CMAKE_ASM_NASM_FLAGS_RELWITHDEBINFO:STRING=

// Choose the type of build, options are: None(CMAKE_CXX_FLAGS or CMAKE_C_FLAGS
used) Debug Release RelWithDebInfo MinSizeRel.
CMAKE_BUILD_TYPE:STRING=

// Enable/Disable color output during build.
CMAKE_COLOR_MAKEFILE:BOOL=ON

// CXX compiler
CMAKE_CXX_COMPILER:FILEPATH=/usr/bin/c++

// Flags used by the compiler during all build types.
CMAKE_CXX_FLAGS:STRING=

// Flags used by the compiler during debug builds.
CMAKE_CXX_FLAGS_DEBUG:STRING=-g

// Flags used by the compiler during release builds for minimum size.
CMAKE_CXX_FLAGS_MINSIZEREL:STRING=-Os -DNDEBUG

// Flags used by the compiler during release builds.
CMAKE_CXX_FLAGS_RELEASE:STRING=-O3 -DNDEBUG

// Flags used by the compiler during release builds with debug info.
CMAKE_CXX_FLAGS_RELWITHDEBINFO:STRING=-O2 -g -DNDEBUG

// C compiler
CMAKE_C_COMPILER:FILEPATH=/usr/bin/cc

// Flags used by the compiler during all build types.
CMAKE_C_FLAGS:STRING=

// Flags used by the compiler during debug builds.
CMAKE_C_FLAGS_DEBUG:STRING=-g

// Flags used by the compiler during release builds for minimum size.
CMAKE_C_FLAGS_MINSIZEREL:STRING=-Os -DNDEBUG

// Flags used by the compiler during release builds.
CMAKE_C_FLAGS_RELEASE:STRING=-O3 -DNDEBUG

// Flags used by the compiler during release builds with debug info.
CMAKE_C_FLAGS_RELWITHDEBINFO:STRING=-O2 -g -DNDEBUG

// Flags used by the linker.
CMAKE_EXE_LINKER_FLAGS:STRING=

// Flags used by the linker during debug builds.
CMAKE_EXE_LINKER_FLAGS_DEBUG:STRING=

// Flags used by the linker during release minsize builds.
CMAKE_EXE_LINKER_FLAGS_MINSIZEREL:STRING=

// Flags used by the linker during release builds.
CMAKE_EXE_LINKER_FLAGS_RELEASE:STRING=

// Flags used by the linker during Release with Debug Info builds.
CMAKE_EXE_LINKER_FLAGS_RELWITHDEBINFO:STRING=

// Enable/Disable output of compile commands during generation.
CMAKE_EXPORT_COMPILE_COMMANDS:BOOL=OFF

// Install path prefix, prepended onto install directories.
CMAKE_INSTALL_PREFIX:PATH=//usr/local/includeos/

// Path to a program.
CMAKE_LINKER:FILEPATH=/usr/bin/ld

// Path to a program.
CMAKE_MAKE_PROGRAM:FILEPATH=/usr/bin/make

// Flags used by the linker during the creation of modules.
CMAKE_MODULE_LINKER_FLAGS:STRING=

// Flags used by the linker during debug builds.
CMAKE_MODULE_LINKER_FLAGS_DEBUG:STRING=

// Flags used by the linker during release minsize builds.
CMAKE_MODULE_LINKER_FLAGS_MINSIZEREL:STRING=

// Flags used by the linker during release builds.
CMAKE_MODULE_LINKER_FLAGS_RELEASE:STRING=

// Flags used by the linker during Release with Debug Info builds.
CMAKE_MODULE_LINKER_FLAGS_RELWITHDEBINFO:STRING=

// Path to a program.
CMAKE_NM:FILEPATH=/usr/bin/nm

// Path to a program.
CMAKE_OBJCOPY:FILEPATH=/usr/bin/objcopy

// Path to a program.
CMAKE_OBJDUMP:FILEPATH=/usr/bin/objdump

// Path to a program.
CMAKE_RANLIB:FILEPATH=/usr/bin/ranlib

// Flags used by the linker during the creation of dll's.
CMAKE_SHARED_LINKER_FLAGS:STRING=

// Flags used by the linker during debug builds.
CMAKE_SHARED_LINKER_FLAGS_DEBUG:STRING=

// Flags used by the linker during release minsize builds.
CMAKE_SHARED_LINKER_FLAGS_MINSIZEREL:STRING=

// Flags used by the linker during release builds.
CMAKE_SHARED_LINKER_FLAGS_RELEASE:STRING=

// Flags used by the linker during Release with Debug Info builds.
CMAKE_SHARED_LINKER_FLAGS_RELWITHDEBINFO:STRING=

// If set, runtime paths are not added when installing shared libraries, but are
added when building.
CMAKE_SKIP_INSTALL_RPATH:BOOL=NO

// If set, runtime paths are not added when using shared libraries.
CMAKE_SKIP_RPATH:BOOL=NO

// Flags used by the linker during the creation of static libraries.
CMAKE_STATIC_LINKER_FLAGS:STRING=

// Flags used by the linker during debug builds.
CMAKE_STATIC_LINKER_FLAGS_DEBUG:STRING=

// Flags used by the linker during release minsize builds.
CMAKE_STATIC_LINKER_FLAGS_MINSIZEREL:STRING=

// Flags used by the linker during release builds.
CMAKE_STATIC_LINKER_FLAGS_RELEASE:STRING=

// Flags used by the linker during Release with Debug Info builds.
CMAKE_STATIC_LINKER_FLAGS_RELWITHDEBINFO:STRING=

// Path to a program.
CMAKE_STRIP:FILEPATH=/usr/bin/strip

// The CMake toolchain file
CMAKE_TOOLCHAIN_FILE:FILEPATH=${INCLUDEOS_SRC}/cmake/elf-toolchain.cmake

// If this value is on, makefiles will be generated without the .SILENT
directive, and all commands will be echoed to the console during the make.  This
is useful for debugging only. With Visual Studio IDE projects all commands are
done without /nologo.
CMAKE_VERBOSE_MAKEFILE:BOOL=FALSE

// Enable to build RPM source packages
CPACK_SOURCE_RPM:BOOL=OFF

// Enable to build TBZ2 source packages
CPACK_SOURCE_TBZ2:BOOL=ON

// Enable to build TGZ source packages
CPACK_SOURCE_TGZ:BOOL=ON

// Enable to build TXZ source packages
CPACK_SOURCE_TXZ:BOOL=ON

// Enable to build TZ source packages
CPACK_SOURCE_TZ:BOOL=ON

// Enable to build ZIP source packages
CPACK_SOURCE_ZIP:BOOL=OFF

// Git command line client
GIT_EXECUTABLE:FILEPATH=/usr/bin/git

// Install with solo5 support
WITH_SOLO5:BOOL=ON

// Restrict use of CPU features to vanilla
cpu_feat_vanilla:BOOL=ON

// Build with no optimizations
debug:BOOL=OFF

// Build and install memdisk helper tool
diskbuilder:BOOL=ON

// Build example unikernels in /examples
examples:BOOL=OFF

// Enable full LTO (compatibility)
full_lto:BOOL=OFF

// Install lest unittest headers
lest:BOOL=OFF

// Build and install LiveUpdate
libliveupdate:BOOL=ON

// Build and install mana web application framework library
libmana:BOOL=ON

// Build and install mender client
libmender:BOOL=ON

// Build and install microLB
libmicroLB:BOOL=ON

// Build and install Google's protobuf runtime library
libprotobuf:BOOL=ON

// Build and install uplink
libuplink:BOOL=ON

// Build for minimal size
minimal:BOOL=OFF

// Disable most output during OS boot
silent:BOOL=OFF

// Compile with SMP (multiprocessing)
smp:BOOL=OFF

// reduce size
stripped:BOOL=OFF

// Build unit tests in /test and install lest test framework
tests:BOOL=OFF

// Enable the Thin LTO plugin
thin_lto:BOOL=OFF

// Enable undefined-behavior sanitizer
undefined_san:BOOL=OFF

// Build and install vmbuild and elf_syms
vmbuild:BOOL=ON
```

In most options we can use the default values, but setting the `CMAKE_INSTALL_PREFIX` to a different directory than `/usr/local/includeos` could be a good advice.

### Step 1: Cloning and preparing the build directory

```
git clone git@github.com:TUM-DSE/funky-unikernel.git
mkdir includeos ## the directory wherre we want to install IncludeOS
export INCLUDEOS_PREFIX=${PWD}/includeos
cd funky-unikernel 
mkdir build && cd build ## The build directory
export CC=clang-5.0
export CXX=clang++-5.0
```

### Step 2: Building IncludeOS

In this step we can define the desired option to build IncludeOS using cmake. We can use most of the default values, except install directory. Moreover to reduce
the build time, IncludeOS provides some of the libraries precompiled and we can
just fetch them. To do that we have to use the target `PrecompiledLibraries` in
make, before start building. Otherwise all the libraries will be compiled from
source.

```
cmake .. -DCMAKE_INSTALL_PREFIX=${INCLUDEOS_PREFIX} 
make PrecompiledLibraries
make -j4
make install 
```

### Step 3 (Optional): Build the chainloader for QEMU

InludeOS generates a 64-bit elf binary, which is not possible to boot in QEMU,
as long as QEMU can boot only 32-bit multiboot images. More information about
boot process of IncludeOS can be found
[here](https://includeos.readthedocs.io/en/latest/The-boot-process.html)
(This documentation does not seem up to date though). Subsequently, there is a
need for a 32 bit image to boot in QEMU. In the case of IncludeOS this is done by
the
[chainloader](https://github.com/includeos/IncludeOS/tree/v0.14.1/src/chainload)
. We can download a precompiled chainloader:

```
curl -L -o $INCLUDEOS_PREFIX/includeos/chainloader https://github.com/fwsGonzo/barebones/releases/download/v0.9-cl/chainloader
```

Otherwise we can build it from source which we will require to build IncludeOS
for i686 too. The reason behind this is that as we said in the beginning the
chainloader should be a 32-bit binary.

```
export PLATFORM=x86_nano
export ARCH=i686
cd {path_to_funky-unikernel}
mkdir build_i686 && cd build_i686
cmake .. -DCMAKE_INSTALL_PREFIX=${INCLUDEOS_PREFIX}
make -j4
make install
cd {path_to_funky}/src/chainload
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=${INCLUDEOS_PREFIX}
make install
```
 
### Step 4: Building the app

We will build a simple hello world example. We will need to create a cmake file
for our application. Browsing the [examples](https://github.com/includeos/IncludeOS/tree/v0.14.1/examples)
directory of IncludeOS we can find some cmake files we can use as a base.

For a simple hello world example the following cmake file is enough.

```
cmake_minimum_required(VERSION 2.8.9)

# IncludeOS install location
if (NOT DEFINED ENV{INCLUDEOS_PREFIX})
  set(ENV{INCLUDEOS_PREFIX} /usr/local)
endif()
include($ENV{INCLUDEOS_PREFIX}/includeos/pre.service.cmake)
project (hello)

# Human-readable name of your service
set(SERVICE_NAME "IncludeOS Hello test")

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
set(DRIVERS
    #virtionet     # Virtio networking
    # virtioblock # Virtio block device
    # ... Others from src/drivers
  )
##endif()

set(PLUGINS
  )

# include service build script
include($ENV{INCLUDEOS_PREFIX}/includeos/post.service.cmake)
```

In that step we specify which drivers and plugins are needed for our application. Furthermore using a 'config.json' file we can configure the network of our unikernel. An example of config can be found [here](https://github.com/includeos/IncludeOS/blob/v0.14.1/examples/demo_service/config.json). We
will deploy our unikernel in QEMU and we do not need any driver or a plugin for
such a simple application. 

```
mkdir build && cd build
cmake ..
make
```

The result will be a `hello.bin` elf 64-bit executable.

### Step 5: Deploy IncludeOS with QEMU

The way to use the result of previous step is giving it as an argunment in QEMU
with the option of `-initrd`. Moreover we need to give the respective kernel
argument. 

```
qemu-system-x86_64 -cpu host -enable-kvm -m 32 -nodefaults -display none -serial stdio -kernel ${INCLUDEOS_PREFIX}/includeos/chainloader -initrd hello.bin -append "-initrd hello.bin" 
```
