/**
* Copyright (C) 2019-2021 Xilinx, Inc
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
#include <os>

// OpenCL utility layer include
#include "xcl2/xcl2.hpp"
#include <algorithm>
#include <cstdio>
#include <random>
#include <vector>
#include <iomanip>

using std::default_random_engine;
using std::generate;
using std::uniform_int_distribution;
using std::vector;

void matmul(int* C, int* A, int* B, int M) {
    for (int k = 0; k < M; k++) {
        for (int j = 0; j < M; j++) {
            for (int i = 0; i < M; i++) {
                C[k * M + j] += A[k * M + i] * B[i * M + j];
            }
        }
    }
}

int gen_random() {
    static default_random_engine e;
    static uniform_int_distribution<int> dist(0, 10);

    return dist(e);
}

void print(int* data, int columns, int rows) {
    vector<int> out(columns * rows);
    for (int r = 0; r < 10; r++) {
        for (int c = 0; c < 10; c++) {
            std::cout << std::setw(4) << data[r * columns + c] << " ";
        }
        std::cout << "…\n";
    }
    for (int r = 0; r < 10; r++) {
        std::cout << "   … ";
    }
    std::cout << "⋱\n\n";
}

void verify(vector<int, aligned_allocator<int> >& gold, vector<int, aligned_allocator<int> >& output) {
    for (int i = 0; i < (int)output.size(); i++) {
        if (output[i] != gold[i]) {
            std::cout << "Mismatch " << i << ": gold: " << gold[i] << " device: " << output[i] << "\n";
            print(output.data(), 16, 16);
            exit(EXIT_FAILURE);
        }
    }
}

// This example illustrates how to use array partitioning attributes in HLS
// kernels for FPGA devices using matmul.
int main(int argc, char** argv) {
    uint32_t repeat_counter = xcl::is_hw_emulation() ? 2 : 1000000;

    if (argc != 2) {
        std::cout << "Usage: " << argv[0] << " <XCLBIN File>" << std::endl;
        return EXIT_FAILURE;
    }
    std::string binaryFile = argv[1];
    static const int columns = 16;
    static const int rows = 16;
    cl_int err;
    cl::CommandQueue q;
    cl::Context context;
    cl::Kernel matmul_kernel, matmul_partition_kernel;
    cl::Program program;
    vector<int, aligned_allocator<int> > A(columns * rows);
    vector<int, aligned_allocator<int> > B(columns * rows);
    vector<int, aligned_allocator<int> > gold(columns * rows, 0);
    vector<int, aligned_allocator<int> > C(columns * rows, 0);
    generate(begin(A), end(A), gen_random);
    generate(begin(B), end(B), gen_random);

    std::cout << "A:\n";
    print(A.data(), columns, rows);
    std::cout << "B:\n";
    print(B.data(), columns, rows);
    matmul(gold.data(), A.data(), B.data(), columns);

    std::cout << "Gold:\n";
    print(gold.data(), columns, rows);
    auto devices = xcl::get_xil_devices();

    // read_binary_file() is a utility API which will load the binaryFile
    // and will return the pointer to file buffer.
    auto fileBuf = xcl::read_binary_file(binaryFile);
    cl::Program::Binaries bins{{fileBuf.data(), fileBuf.size()}};
    bool valid_device = false;
    for (unsigned int i = 0; i < devices.size(); i++) {
        auto device = devices[i];
        // Creating Context and Command Queue for selected Device
        OCL_CHECK(err, context = cl::Context(device, nullptr, nullptr, nullptr, &err));
        OCL_CHECK(err, q = cl::CommandQueue(context, device, CL_QUEUE_PROFILING_ENABLE, &err));

        std::cout << "Trying to program device[" << i << "]: " << device.getInfo<CL_DEVICE_NAME>() << std::endl;
        program = cl::Program(context, {device}, bins, nullptr, &err);
        if (err != CL_SUCCESS) {
            std::cout << "Failed to program device[" << i << "] with xclbin file!\n";
        } else {
            std::cout << "Device[" << i << "]: program successful!\n";
            valid_device = true;
            break; // we break because we found a valid device
        }
    }
    if (!valid_device) {
        std::cout << "Failed to program any device found, exit!\n";
        exit(EXIT_FAILURE);
    }

    // compute the size of array in bytes
    size_t array_size_bytes = columns * rows * sizeof(int);
    OCL_CHECK(err,
              cl::Buffer buffer_a(context, CL_MEM_USE_HOST_PTR | CL_MEM_READ_ONLY, array_size_bytes, A.data(), &err));
    OCL_CHECK(err,
              cl::Buffer buffer_b(context, CL_MEM_USE_HOST_PTR | CL_MEM_READ_ONLY, array_size_bytes, B.data(), &err));
    OCL_CHECK(err,
              cl::Buffer buffer_c(context, CL_MEM_USE_HOST_PTR | CL_MEM_WRITE_ONLY, array_size_bytes, C.data(), &err));

    std::cout << "|-------------------------+-------------------------|\n"
              << "| Kernel                  |    Wall-Clock Time (ns) |\n"
              << "|-------------------------+-------------------------|\n";

    OCL_CHECK(err, matmul_kernel = cl::Kernel(program, "matmul", &err));
    OCL_CHECK(err, err = matmul_kernel.setArg(0, buffer_a));
    OCL_CHECK(err, err = matmul_kernel.setArg(1, buffer_b));
    OCL_CHECK(err, err = matmul_kernel.setArg(2, buffer_c));
    OCL_CHECK(err, err = matmul_kernel.setArg(3, columns));
    OCL_CHECK(err, err = matmul_kernel.setArg(4, repeat_counter));

    OCL_CHECK(err, err = q.enqueueMigrateMemObjects({buffer_a, buffer_b}, 0 /* 0 means from host*/));

    cl::Event event;
    uint64_t nstimestart, nstimeend;

    OCL_CHECK(err, err = q.enqueueTask(matmul_kernel, nullptr, &event));
    OCL_CHECK(err, err = q.enqueueMigrateMemObjects({buffer_c}, CL_MIGRATE_MEM_OBJECT_HOST));
    q.finish();

    OCL_CHECK(err, err = event.getProfilingInfo<uint64_t>(CL_PROFILING_COMMAND_START, &nstimestart));
    OCL_CHECK(err, err = event.getProfilingInfo<uint64_t>(CL_PROFILING_COMMAND_END, &nstimeend));
    auto matmul_time = (nstimeend - nstimestart) / repeat_counter;

    verify(gold, C);
    std::cout << "| " << std::left << std::setw(24) << "matmul: "
              << "|" << std::right << std::setw(24) << matmul_time << " |\n";

    OCL_CHECK(err, matmul_partition_kernel = cl::Kernel(program, "matmul_partition", &err));

    OCL_CHECK(err, err = matmul_partition_kernel.setArg(0, buffer_a));
    OCL_CHECK(err, err = matmul_partition_kernel.setArg(1, buffer_b));
    OCL_CHECK(err, err = matmul_partition_kernel.setArg(2, buffer_c));
    OCL_CHECK(err, err = matmul_partition_kernel.setArg(3, columns));
    OCL_CHECK(err, err = matmul_partition_kernel.setArg(4, repeat_counter));

    OCL_CHECK(err, err = q.enqueueTask(matmul_partition_kernel, nullptr, &event));
    OCL_CHECK(err, err = q.enqueueMigrateMemObjects({buffer_c}, CL_MIGRATE_MEM_OBJECT_HOST));
    q.finish();

    OCL_CHECK(err, err = event.getProfilingInfo<uint64_t>(CL_PROFILING_COMMAND_START, &nstimestart));
    OCL_CHECK(err, err = event.getProfilingInfo<uint64_t>(CL_PROFILING_COMMAND_END, &nstimeend));
    auto matmul_partition_time = (nstimeend - nstimestart) / repeat_counter;

    verify(gold, C);

    std::cout << "| " << std::left << std::setw(24) << "matmul: partition"
              << "|" << std::right << std::setw(24) << matmul_partition_time << " |\n";
    std::cout << "|-------------------------+-------------------------|\n";
    std::cout << "| " << std::left << std::setw(24) << "Speedup"
              << "|" << std::right << std::setw(24) << (double)matmul_time / (double)matmul_partition_time << " |\n";
    std::cout << "|-------------------------+-------------------------|\n";
    std::cout << "Note: Wall Clock Time is meaningful for real hardware execution "
              << "only, not for emulation.\n";
    std::cout << "Please refer to profile summary for kernel execution time for "
              << "hardware emulation.\n";
    std::cout << "TEST PASSED\n\n";

    return EXIT_SUCCESS;
}
