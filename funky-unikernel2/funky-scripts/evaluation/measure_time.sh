#!/bin/bash

source ./common.sh

function usage {
  cat <<EOF

Usage: 
  $(basename ${0}) <repeat>

  Measure the end-to-end execution time of workloads in Vitis_Accel_Examples/ and Rosetta/.
  clock_gettime() with MONOTONIC timer is used for the measurement. 

EOF
}

measure_time() {
  arg_benchdir=$1
  # arg_apps_array=$2[@]
  # arg_apps=("${!arg_apps_array}")
  # arg_args_array=$3[@]
  # arg_args=("${!arg_args_array}")
  arg_repeat=$2
  arg_ifile=$3
  arg_ofile=$4

  ### create dir where the results are saved
  RESULTS_DIR="${EVAL_SCRIPT_ROOT}/time_$DATE"
  mkdir -p ${RESULTS_DIR}
  APPLIST_CSV="${EVAL_SCRIPT_ROOT}/${arg_ifile}"
  RESULTS_CSV="${RESULTS_DIR}/${arg_ofile}"

  ### add label to csv 
  echo -n "app_name, " >> ${RESULTS_CSV}
  for loop in $(seq 1 ${arg_repeat}); do
    echo -n "${loop}, " >> ${RESULTS_CSV}
  done
  echo "average, stdev, " >> ${RESULTS_CSV}

  ### execution
  echo "move into ${arg_benchdir}..."
  pushd ${arg_benchdir}

  # python3 ${EVAL_SCRIPT_ROOT}/measure_time.py ${RESULTS_DIR} ${RESULTS_CSV} ${APPLIST_CSV} ${arg_repeat} ${UKVM_EXEC_CMD}
  measure_ukvm_exec_time_py ${RESULTS_DIR} ${RESULTS_CSV} ${APPLIST_CSV} ${arg_repeat} ${UKVM_EXEC_CMD}

  popd
  echo "back to $(pwd)."
}

set_ukvm_permission # make ukvm-bin executable

REPEAT=$1

if [ -z ${REPEAT} ]; then
  usage
  exit -1
fi

DIR="time_$DATE"
mkdir -p ${EVAL_SCRIPT_ROOT}/$DIR

measure_time ${VITIS_EXAMPLES_DIR} ${REPEAT} "vitis_applist.csv" "vitis.csv"
measure_time ${ROSETTA_DIR} ${REPEAT} "rosetta_applist.csv" "rosetta.csv"

