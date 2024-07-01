#!/bin/bash
BUILD_DIR=build/

function usage {
  cat <<EOF
Usage: 
  $(basename ${0}) <build dir>

Options: 
  -h                    print help

  -f                    force build

  -d                    specify build dir
EOF
}

########### get arguments #############
while getopts hfd: OPT
do
  case $OPT in
    "h" )
      usage
      exit -1 ;;
    "f" )
      FORCE_FLAG=true ;;
    "d" )
      BUILD_DIR=${OPTARG} ;;
  esac
done

if [ -z ${BUILD_DIR} ]; then
  usage
  exit -1
fi

if [ -e ${BUILD_DIR} ]; then
  if "${FORCE_FLAG}" ; then
    echo "INFO: the selected directory ${BUILD_DIR}/ already exists. This script will remove it. "
    rm -r ${BUILD_DIR}
  else
    echo "Warning: the selected directory ${BUILD_DIR}/ already exists. This script will remove the old one and re-compile it. "
    read -p "Do you continue?: [y/N]: " yn
    case ${yn} in
      [yY]*) 
        rm -r ${BUILD_DIR}
        ;;
      *) 
        echo "Abort."
        exit -1 ;;
    esac
  fi
fi

mkdir ${BUILD_DIR}
pushd ${BUILD_DIR}
PLATFORM=x86_solo5 cmake -DCMAKE_BUILD_TYPE=Debug ..
make -j 8
popd

