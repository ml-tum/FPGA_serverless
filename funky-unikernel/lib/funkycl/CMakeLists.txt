cmake_minimum_required(VERSION 2.8.9)

add_definitions(-DARCH_${ARCH})
add_definitions(-DARCH="${ARCH}")

include_directories(${INCLUDEOS_ROOT}/api/posix)
include_directories(${LIBCXX_INCLUDE_DIR})
include_directories(${MUSL_INCLUDE_DIR})
include_directories(${INCLUDEOS_ROOT}/src/include)
include_directories(${INCLUDEOS_ROOT}/api)
include_directories(${INCLUDEOS_ROOT}/mod/GSL/)

# include_directories(${INCLUDEOS_ROOT}/lib/funkycl/include/funkycl_lib)
include_directories(${INCLUDEOS_ROOT}/lib/funkycl/include)
# include_directories(${INCLUDEOS_ROOT}/lib/funkycl/common)
include_directories(${INCLUDEOS_ROOT}/lib/funkycl/backend)
include_directories(${INCLUDEOS_ROOT}/lib/funkycl/)

set(LIBRARY_NAME "funkycl")

set(FUNKYCL_OBJECT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/object")
set(FUNKYCL_API_DIR "${CMAKE_CURRENT_SOURCE_DIR}/api")

file(GLOB FUNKYCL_OBJECT_FILES
  "${FUNKYCL_OBJECT_DIR}/*.h"
  "${FUNKYCL_OBJECT_DIR}/*.cpp"
  )

file(GLOB FUNKYCL_API_FILES
  "${FUNKYCL_API_DIR}/*.h"
  "${FUNKYCL_API_DIR}/*.cpp"
  )

set(SOURCES
  ${FUNKYCL_OBJECT_FILES}
  # funkycl.cpp
  ${FUNKYCL_API_FILES}
  )

# LiveUpdate static library
add_library(${LIBRARY_NAME} STATIC ${SOURCES})
add_dependencies(${LIBRARY_NAME} PrecompiledLibraries)

install(TARGETS ${LIBRARY_NAME} DESTINATION includeos/${ARCH}/lib)
# install(DIRECTORY include/funkycl_lib DESTINATION includeos/include)
install(DIRECTORY include/CL DESTINATION includeos/include)
