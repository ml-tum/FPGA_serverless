#!/bin/bash
set -e

if [ "$1" == "" ]; then
        echo "Usage: Pass descriptor filename (without '.yml') as parameter."
    exit
fi
if [ ! -f "$1.yml" ]; then
    echo "$1.yml does not exist."
    exit
fi

faas-cli build --shrinkwrap -f $1.yml

if [ "$1" == "hls4ml-cpu" ]; then
    sudo buildctl build --frontend dockerfile.v0 --local context=./build/$1/ --local dockerfile=./build/$1/ --output type=image,name=docker.io/ccgroup47/myrepo:$1,push=true
else
    sudo buildctl build --frontend dockerfile.v0 --local context=./$1/ --local dockerfile=./$1/ --output type=image,name=docker.io/ccgroup47/myrepo:$1,push=true
fi
