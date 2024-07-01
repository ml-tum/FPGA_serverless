# how to measure hypercall overhead
  git clone git@github.com:TUM-DSE/funky-monitor.git
  cd funky-monitor/vfpga-dev
  make FUNKY_MACROS=-DEVAL_HYPERCALL_OH

  cd <here>
  ./build.sh build
  ./execute.sh build ~/funky-monitor/ukvm/ukvm-bin > hypercall_oh.csv

