#!/bin/bash
set -e

export CPP_FILE="src/$1.cpp"
if [ "$1" == "" ]; then
	echo "Usage: Pass source code filename (without '.cpp') as parameter."
    exit
fi
if [ ! -f "$CPP_FILE" ]; then
    echo "$CPP_FILE does not exist."
    exit
fi

rm -rf build
mkdir build
pushd build
export INCLUDEOS_PREFIX=~/includeos
export PLATFORM=x86_solo5
cmake ..
make -j64
popd

#docker build -t docker.io/ccgroup47/myrepo:$1 .
#docker image push docker.io/ccgroup47/myrepo:$1
sudo DOCKER_CONFIG=/home/martin/.docker /home/martin/bin/buildctl build --frontend dockerfile.v0 --local context=. --local dockerfile=. --output type=image,name=docker.io/ccgroup47/myrepo:$1,push=true
