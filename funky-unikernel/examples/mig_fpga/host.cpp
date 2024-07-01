/**
* Copyright (C) 2020 Xilinx, Inc
*
* Licensed under the Apache License, Version 2.0 (the "License"). You may
* not use this file except in compliance with the License. A copy of the
* License is located at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
* License for the specific language governing permissions and limitations
* under the License.
*/

// FunkyOS
#include <os> // IncludeOS

#include <cstdio>
#include <unistd.h>

#include "timer.h"

#include "xcl2/xcl2.hpp"
#include <algorithm>
#include <vector>
// #define DATA_SIZE 4096
// #define DATA_SIZE 16*1024*1024
#define DATA_SIZE 20*1024*1024

// #define MIGRATION

TIMER_INIT(10);
// TIMER_INIT(9);

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cout << "Usage: " << argv[0] << " <XCLBIN File>" << std::endl;
        return EXIT_FAILURE;
    }

    std::string binaryFile = argv[1];
    size_t vector_size_bytes = sizeof(int) * DATA_SIZE;
    cl_int err;
    cl::Context context;
    cl::Kernel krnl_vector_add;
    cl::CommandQueue q;
    // Allocate Memory in Host Memory
    // When creating a buffer with user pointer (CL_MEM_USE_HOST_PTR), under the
    // hood user ptr
    // is used if it is properly aligned. when not aligned, runtime had no choice
    // but to create
    // its own host side buffer. So it is recommended to use this allocator if
    // user wish to
    // create buffer using CL_MEM_USE_HOST_PTR to align user buffer to page
    // boundary. It will
    // ensure that user buffer is used when user create Buffer/Mem object with
    // CL_MEM_USE_HOST_PTR

    // TIMER_START(9);
    std::vector<int, aligned_allocator<int> > source_in1(DATA_SIZE);
    std::vector<int, aligned_allocator<int> > source_in2(DATA_SIZE);
    std::vector<int, aligned_allocator<int> > source_hw_results(DATA_SIZE);
    std::vector<int, aligned_allocator<int> > source_sw_results(DATA_SIZE);

    // Create the test data
    std::generate(source_in1.begin(), source_in1.end(), std::rand);
    std::generate(source_in2.begin(), source_in2.end(), std::rand);
    for (int i = 0; i < DATA_SIZE; i++) {
        source_sw_results[i] = source_in1[i] + source_in2[i];
        source_hw_results[i] = 0;
    }
    // TIMER_STOP_ID(9);

#ifdef MIGRATION
    /* Checkpoint 1: Worker thread is not created */
    std::cout << "[Guest] checkpoint 1: waiting..." << std::endl;
    uint64_t cnt=0;
    while(cnt < 10000000000)
      cnt++;
#endif

    TIMER_START(0); // total time (exclude input/output data initialization)

    TIMER_START(1);
    // OPENCL HOST CODE AREA START
    // get_xil_devices() is a utility API which will find the xilinx
    // platforms and will return list of devices connected to Xilinx platform
    auto devices = xcl::get_xil_devices();
    // read_binary_file() is a utility API which will load the binaryFile
    // and will return the pointer to file buffer.
    auto fileBuf = xcl::read_binary_file(binaryFile);
    cl::Program::Binaries bins{{fileBuf.data(), fileBuf.size()}};
    TIMER_STOP_ID(1);

    // TIMER_STOP;

    bool valid_device = false;
    for (unsigned int i = 0; i < devices.size(); i++) {
        auto device = devices[i];

        TIMER_START(9); // total time (exclude input/output data initialization and open a file)

        TIMER_START(2);
        // Creating Context and Command Queue for selected Device
        OCL_CHECK(err, context = cl::Context(device, nullptr, nullptr, nullptr, &err));
        OCL_CHECK(err, q = cl::CommandQueue(context, device, CL_QUEUE_PROFILING_ENABLE, &err));
        // std::cout << "Trying to program device[" << i << "]: " << device.getInfo<CL_DEVICE_NAME>() << std::endl;

        cl::Program program(context, {device}, bins, nullptr, &err);
        q.finish();
        TIMER_STOP_ID(2);

        // std::cout << "BBBBBBBBBBBBBBBBBBBBBBBB\n";

        if (err != CL_SUCCESS) {
            std::cout << "Failed to program device[" << i << "] with xclbin file!\n";
        } else {
            std::cout << "Device[" << i << "]: program successful!\n";

            TIMER_START(3);
            OCL_CHECK(err, krnl_vector_add = cl::Kernel(program, "vadd", &err));
            TIMER_STOP_ID(3);

            valid_device = true;
            break; // we break because we found a valid device
        }
    }
    if (!valid_device) {
        std::cout << "Failed to program any device found, exit!\n";
        exit(EXIT_FAILURE);
    }

#ifdef MIGRATION
    /* Checkpoint 2: Worker thread is created but any data is sent to FPGA */
    q.finish();
    std::cout << "[Guest] checkpoint 2: waiting..." << std::endl;
    cnt=0;
    while(cnt < 10000000000)
      cnt++;
#endif

    // Allocate Buffer in Global Memory
    // Buffers are allocated using CL_MEM_USE_HOST_PTR for efficient memory and
    // Device-to-host communication
    TIMER_START(4);
    OCL_CHECK(err, cl::Buffer buffer_in1(context, CL_MEM_USE_HOST_PTR | CL_MEM_READ_ONLY, vector_size_bytes,
                                         source_in1.data(), &err));
    OCL_CHECK(err, cl::Buffer buffer_in2(context, CL_MEM_USE_HOST_PTR | CL_MEM_READ_ONLY, vector_size_bytes,
                                         source_in2.data(), &err));
    OCL_CHECK(err, cl::Buffer buffer_output(context, CL_MEM_USE_HOST_PTR | CL_MEM_WRITE_ONLY, vector_size_bytes,
                                            source_hw_results.data(), &err));
    TIMER_STOP(4);

    TIMER_START(5);
    int size = DATA_SIZE;
    OCL_CHECK(err, err = krnl_vector_add.setArg(0, buffer_in1));
    OCL_CHECK(err, err = krnl_vector_add.setArg(1, buffer_in2));
    OCL_CHECK(err, err = krnl_vector_add.setArg(2, buffer_output));
    OCL_CHECK(err, err = krnl_vector_add.setArg(3, size));
    TIMER_STOP(5);

    TIMER_START(6);
    // Copy input data to device global memory
    OCL_CHECK(err, err = q.enqueueMigrateMemObjects({buffer_in1, buffer_in2}, 0 /* 0 means from host*/));
    q.finish();
    TIMER_STOP(6);


#ifdef MIGRATION
    /* Checkpoint 3: Worker thread is created and input data are sent to FPGA */
    std::cout << "[Guest] checkpoint 3: waiting..." << std::endl;
    q.finish();
    uint64_t cnt=0;
    while(cnt < 10000000000)
      cnt++;
#endif

    // Launch the Kernel
    // For HLS kernels global and local size is always (1,1,1). So, it is
    // recommended
    // to always use enqueueTask() for invoking HLS kernel
    TIMER_START(7);
    OCL_CHECK(err, err = q.enqueueTask(krnl_vector_add));
    q.finish();
    TIMER_STOP(7);

    // Copy Result from Device Global Memory to Host Local Memory
    TIMER_START(8);
    OCL_CHECK(err, err = q.enqueueMigrateMemObjects({buffer_output}, CL_MIGRATE_MEM_OBJECT_HOST));
    q.finish();
    TIMER_STOP(8);
    // OPENCL HOST CODE AREA END

    TIMER_STOP_ID(0); // end total time
    TIMER_STOP_ID(9); // end total time

    // Compare the results of the Device to the simulation
    bool match = true;
    for (int i = 0; i < DATA_SIZE; i++) {
        if (source_hw_results[i] != source_sw_results[i]) {
            std::cout << "Error: Result mismatch" << std::endl;
            std::cout << "i = " << i << " CPU result = " << source_sw_results[i]
                      << " Device result = " << source_hw_results[i] << std::endl;
            match = false;
            break;
        }
    }

    std::cout << "TEST " << (match ? "PASSED" : "FAILED") << std::endl;

    printf("------------------------------------------------------\n");
    printf("  Performance Summary                                 \n");
    printf("------------------------------------------------------\n");
    // printf("  Input data generation      : %12.4f ms\n", TIMER_REPORT_MS(9));
    printf("  Open a bitstream file (memdisk) : %12.4f ms\n", TIMER_REPORT_MS(1));
    printf("  Writing Bitstream (init Funky)  : %12.4f ms\n", TIMER_REPORT_MS(2));
    printf("  Kernel Allocation               : %12.4f ms\n", TIMER_REPORT_MS(3));
    printf("  Buffer Allocation               : %12.4f ms\n", TIMER_REPORT_MS(4));
    printf("  Set Kernel arguments            : %12.4f ms\n", TIMER_REPORT_MS(5));
    printf("  Input Data transfer             : %12.4f ms\n", TIMER_REPORT_MS(6));
    printf("  Enqueue Kernel                  : %12.4f ms\n", TIMER_REPORT_MS(7));
    printf("  Output Data transfer            : %12.4f ms\n", TIMER_REPORT_MS(8));
    printf("  Total execution time            : %12.4f ms\n", TIMER_REPORT_MS(0));
    printf("  Total execution time w/o open   : %12.4f ms\n", TIMER_REPORT_MS(9));
    printf("------------------------------------------------------\n");



    return (match ? EXIT_SUCCESS : EXIT_FAILURE);
}
