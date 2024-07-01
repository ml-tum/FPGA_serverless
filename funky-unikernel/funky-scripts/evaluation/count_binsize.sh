#!/bin/bash

source ./common.sh

VITIS_ORIG_DIR=$1
ROSETTA_ORIG_DIR=$2

count_binsize() {
  arg_dir=$1
  arg_orig_dir=$2
  arg_apps_array=$3[@]
  arg_apps=("${!arg_apps_array}")

  echo "app, funky-bin, bitstream, etc, orig-bin"

  for i in ${!arg_apps[@]}; do
    echo -n "${arg_apps[$i]}, "

    # show loc
    cd ${arg_dir}/${arg_apps[$i]}
    count=`wc -c < ${APP_BIN}`
    BINSIZE=`echo ${count} | xargs`
    echo -n "${BINSIZE}, "

    # get 
    # RAWFILES=`ls ${EVAL_SCRIPT_ROOT}/../../xclbin/u50/${arg_apps[$i]} | awk '{print "< " $1}' | xargs`
    # TMP=0; for i in `ls` ; do data=`wc -c < ${i}`; TMP=$TMP+$data ; done ; echo $TMP | bc
    cd ${EVAL_SCRIPT_ROOT}/../../xclbin/u50/${arg_apps[$i]}

    SUM=0
    for file in `find -name "*.xclbin"`; do 
      filesize=`wc -c < ${file}`
      SUM=${SUM}+${filesize}
    done
    BS_SIZE=`echo ${SUM} | bc`
    echo -n "${BS_SIZE}, "

    # for file in `ls`; do 
    SUM=0
    for file in `find -name "*" -type f`; do 
      filesize=`wc -c < ${file}`
      SUM=${SUM}+${filesize}
    done
    RAWFILESIZE=`echo ${SUM} | bc`
    echo -n "${RAWFILESIZE}, "

    # echo "${arg_orig_dir}/${arg_apps[$i]}"
    cd ${arg_orig_dir}/${arg_apps[$i]}
    TMP=`wc -c < ${arg_apps[$i]}`
    echo ${TMP} | xargs

    # if [ ${arg_dir} = ${VITIS_EXAMPLES_DIR} ]; then
    #   # show 
    # else
    #   # show 
    #   TMP=`wc -c < ${ROSETTA_BINS[$i]}`
    #   echo ${TMP} | xargs
    # fi

  done 
}

count_binsize ${VITIS_EXAMPLES_DIR} ${VITIS_ORIG_DIR} VITIS_EXAMPLES_APPS
count_binsize ${ROSETTA_DIR} ${ROSETTA_ORIG_DIR} ROSETTA_APPS

