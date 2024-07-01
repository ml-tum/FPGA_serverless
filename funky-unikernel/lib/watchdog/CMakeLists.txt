cmake_minimum_required(VERSION 2.8.9)

add_definitions(-DARCH_${ARCH})
add_definitions(-DARCH="${ARCH}")

#dependencies. We specify all other IncludeOS' components and standard
#libraries. In case that we have more depedencies like other external libraries
#we have to specify the library here.
include_directories(${INCLUDEOS_ROOT}/api/posix)
include_directories(${LIBCXX_INCLUDE_DIR})
include_directories(${MUSL_INCLUDE_DIR})
include_directories(${INCLUDEOS_ROOT}/src/include)
include_directories(${INCLUDEOS_ROOT}/api)
include_directories(${INCLUDEOS_ROOT}/mod/GSL/)

set(LIBRARY_NAME "watchdog")

set(SOURCES
  src/watchdog.cpp
  )

add_library(${LIBRARY_NAME} STATIC ${SOURCES})
#We need to specify any build time depedencies. Maybe an another library we need
#has to be built first.
add_dependencies(${LIBRARY_NAME} PrecompiledLibraries)

install(TARGETS ${LIBRARY_NAME} DESTINATION includeos/${ARCH}/lib)
