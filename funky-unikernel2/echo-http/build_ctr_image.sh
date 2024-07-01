#!/bin/bash
set -e

rm -rf build
mkdir build
pushd build
export INCLUDEOS_PREFIX=~/includeos
export PLATFORM=x86_solo5
cmake ..
make -j64
popd
docker build --no-cache -t docker.io/ccgroup47/myrepo:echo-http .
docker image push docker.io/ccgroup47/myrepo:echo-http
