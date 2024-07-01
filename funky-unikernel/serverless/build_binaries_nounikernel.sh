#!/bin/bash
set -e

cat src-files.txt | while read line 
do
    name=$line
    name=${name##*/}
    name=${name%.cpp}
    g++ -std=c++17 -o no_unikernel/$name "$line" -DNO_UNIKERNEL
done
