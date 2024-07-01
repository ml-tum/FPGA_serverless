#!/bin/bash

source ./common.sh

VITIS_ORIG_DIR=$1
ROSETTA_ORIG_DIR=$2

count_loc() {
  arg_dir=$1
  arg_orig_dir=$2
  arg_apps_array=$3[@]
  arg_apps=("${!arg_apps_array}")

  for i in ${!arg_apps[@]}; do
    app=${arg_apps[$i]}
    echo "count ${app}..."
    cd ${arg_dir}/${app}

    LOG="${EVAL_SCRIPT_ROOT}/${DIR}/${arg_apps[$i]}.log"
    CSV="${EVAL_SCRIPT_ROOT}/${DIR}/${arg_apps[$i]}.csv"

    HOSTCODE="host.cpp"
    HOSTCODE_DIR="src"
    if [ ${app} = "simple_vadd" ]; then
      HOSTCODE="vadd.cpp"
    elif [ ${arg_dir} = ${ROSETTA_DIR} ]; then
      HOSTCODE=""
      HOSTCODE_DIR="src/host"
    fi

    COMMIT=`git rev-parse HEAD` # get commit hash
    echo "${apps}, ${COMMIT}" >> ${CSV}
    # LOC of orig code
    # cloc --quiet ${arg_orig_dir}/${app}/${HOSTCODE_DIR}/${HOSTCODE} ${arg_orig_dir}/${app}/${HOSTCODE_DIR}/*.h --include-lang=C/C++\ Header,C,C++ --exclude-dir=build --by-file | tee ${LOG}
    # cloc --quiet ${arg_orig_dir}/${app}/${HOSTCODE_DIR}/${HOSTCODE} ${arg_orig_dir}/${app}/${HOSTCODE_DIR}/*.h --include-lang=C/C++\ Header,C,C++ --exclude-dir=build --by-file --csv >> ${CSV}

    cloc --quiet ${arg_dir}/${app}/${HOSTCODE} ${arg_dir}/${app}/*.h --include-lang=C/C++\ Header,C,C++ --exclude-dir=build --by-file | tee ${LOG}
    cloc --quiet ${arg_dir}/${app}/${HOSTCODE} ${arg_dir}/${app}/*.h --include-lang=C/C++\ Header,C,C++ --exclude-dir=build --by-file --csv >> ${CSV}

    echo "code changes for Funky" >> ${CSV}
    cloc --quiet --diff ${arg_orig_dir}/${app}/${HOSTCODE_DIR}/${HOSTCODE} ${arg_dir}/${app}/${HOSTCODE} --include-lang=C/C++\ Header,C,C++ --exclude-dir=build --by-file | tee ${LOG}
    cloc --quiet --diff ${arg_orig_dir}/${app}/${HOSTCODE_DIR}/${HOSTCODE} ${arg_dir}/${app}/${HOSTCODE} --include-lang=C/C++\ Header,C,C++ --exclude-dir=build --by-file --csv >> ${CSV}
  done

  # additional count for common lib
  if [ ${arg_dir} = ${VITIS_EXAMPLES_DIR} ]; then
    LOG="${EVAL_SCRIPT_ROOT}/${DIR}/funky_utils.log"
    CSV="${EVAL_SCRIPT_ROOT}/${DIR}/funky_utils.csv"

    # LOC of orig code
    # cloc --quiet ${arg_orig_dir}/../common/includes --exclude-dir=oclHelper,opencl,simplebmp --by-file | tee ${LOG}
    # cloc --quiet ${arg_orig_dir}/../common/includes --exclude-dir=oclHelper,opencl,simplebmp --by-file --csv >> ${CSV}

    cloc --quiet ${arg_dir}/../funky_utils --exclude-dir=oclHelper,opencl,simplebmp --by-file | tee ${LOG}
    cloc --quiet ${arg_dir}/../funky_utils --exclude-dir=oclHelper,opencl,simplebmp --by-file --csv >> ${CSV}

    echo "code changes for Funky" >> ${CSV}
    cloc --quiet --diff ${arg_orig_dir}/../common/includes ${arg_dir}/../funky_utils --exclude-dir=oclHelper,opencl,simplebmp --exclude-list-file=timer.h --by-file | tee ${LOG}
    cloc --quiet --diff ${arg_orig_dir}/../common/includes ${arg_dir}/../funky_utils --exclude-dir=oclHelper,opencl,simplebmp --exclude-list-file=timer.h --by-file --csv >> ${CSV}
  else 
    LOG="${EVAL_SCRIPT_ROOT}/${DIR}/harness.log"
    CSV="${EVAL_SCRIPT_ROOT}/${DIR}/harness.csv"

    # cloc --quiet ${arg_orig_dir}/harness/ocl_src --by-file | tee ${LOG}
    # cloc --quiet ${arg_orig_dir}/harness/ocl_src --by-file --csv >> ${CSV}

    cloc --quiet ${arg_dir}/harness --by-file | tee ${LOG}
    cloc --quiet ${arg_dir}/harness --by-file --csv >> ${CSV}

    echo "code changes for Funky" >> ${CSV}
    cloc --quiet --diff ${arg_orig_dir}/harness/ocl_src ${arg_dir}/harness --by-file | tee ${LOG}
    cloc --quiet --diff ${arg_orig_dir}/harness/ocl_src ${arg_dir}/harness --by-file --csv >> ${CSV}
  fi
}

DIR="loc_$DATE"
mkdir -p $DIR

count_loc ${VITIS_EXAMPLES_DIR} ${VITIS_ORIG_DIR} VITIS_EXAMPLES_APPS
count_loc ${ROSETTA_DIR} ${ROSETTA_ORIG_DIR} ROSETTA_APPS

