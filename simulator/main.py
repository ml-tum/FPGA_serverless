import simulator

simulator.run_on_file(
    MAX_REQUESTS=0,
    NUM_NODES=40,
    FUNCTION_KEEPALIVE=None,
    FPGA_RECONFIGURATION_TIME=0.3,
    ENABLE_LOGS=True,
    ENABLE_PROGRESS_LOGS=True,
)