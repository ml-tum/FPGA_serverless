#!/bin/bash

source ./common.sh

build_benchmark() {
  arg_dir=$1
  arg_apps_array=$2[@]
  arg_apps=("${!arg_apps_array}")

  for i in ${!arg_apps[@]}; do
    echo "build ${arg_apps[$i]}..."
    cd ${arg_dir}/${arg_apps[$i]}

    # build
    ./build.sh -d build -f &> /dev/null &
  done 
}

build_benchmark ${VITIS_EXAMPLES_DIR} VITIS_EXAMPLES_APPS
build_benchmark ${ROSETTA_DIR} ROSETTA_APPS

