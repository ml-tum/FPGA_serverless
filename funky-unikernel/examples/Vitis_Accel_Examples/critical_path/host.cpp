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
#include "bitmap/bitmap.h"
#include "cmdparser/cmdlineparser.h"
#include "xcl2/xcl2.hpp"
#include <vector>

int main(int argc, char** argv) {
    // Command Line Parser
    sda::utils::CmdLineParser parser;

    // Switches
    //**************//"<Full Arg>",  "<Short Arg>", "<Description>", "<Default>"
    parser.addSwitch("--xclbin_file", "-x", "input binary file string", "");
    parser.addSwitch("--input_file", "-i", "input test data flie", "");
    parser.addSwitch("--compare_file", "-c", "Compare File to compare result", "");
    parser.parse(argc, argv);

    // Read settings
    auto binaryFile = parser.value("xclbin_file");
    std::string bitmapFilename = parser.value("input_file");
    std::string goldenFilename = parser.value("compare_file");

    if (argc != 7) {
        parser.printHelp();
        return EXIT_FAILURE;
    }

    // Read the input bit map file into memory
    BitmapInterface image(bitmapFilename.data());
    bool result = image.readBitmapFile();
    if (!result) {
        std::cerr << "ERROR:Unable to Read Input Bitmap File " << bitmapFilename.data() << std::endl;
        return EXIT_FAILURE;
    }

    // Read the golden bit map file into memory
    BitmapInterface goldenImage(goldenFilename.data());
    result = goldenImage.readBitmapFile();
    if (!result) {
        std::cerr << "ERROR:Unable to Read Golden Bitmap File " << goldenFilename.data() << std::endl;
        return EXIT_FAILURE;
    }

    int width = image.getWidth();
    int height = image.getHeight();

    // Allocate Memory in Host Memory
    size_t image_size_bytes = image.numPixels() * sizeof(int);
    std::vector<int, aligned_allocator<int> > inImage(image.numPixels());
    std::vector<int, aligned_allocator<int> > outImage(image.numPixels());

    // Copying image host buffer
    memcpy(inImage.data(), image.bitmap(), image_size_bytes);

    // OPENCL HOST CODE AREA START

    int err;
    cl::Context context;
    cl::CommandQueue q;
    cl::Kernel kernel;
    auto devices = xcl::get_xil_devices();
    auto fileBuf = xcl::read_binary_file(binaryFile);
    cl::Program::Binaries bins{{fileBuf.data(), fileBuf.size()}};
    bool valid_device = false;
    for (unsigned int i = 0; i < devices.size(); i++) {
        auto device = devices[i];
        // Creating Context and Command Queue for selected Device
        OCL_CHECK(err, context = cl::Context(device, nullptr, nullptr, nullptr, &err));
        OCL_CHECK(err, q = cl::CommandQueue(context, device, CL_QUEUE_PROFILING_ENABLE, &err));

        std::cout << "Trying to program device[" << i << "]: " << device.getInfo<CL_DEVICE_NAME>() << std::endl;
        cl::Program program(context, {device}, bins, nullptr, &err);
        if (err != CL_SUCCESS) {
            std::cout << "Failed to program device[" << i << "] with xclbin file!\n";
        } else {
            std::cout << "Device[" << i << "]: program successful!\n";
            OCL_CHECK(err, kernel = cl::Kernel(program, "apply_watermark", &err));
            valid_device = true;
            break; // we break because we found a valid device
        }
    }
    if (!valid_device) {
        std::cerr << "Failed to program any device found, exit!\n";
        exit(EXIT_FAILURE);
    }

    OCL_CHECK(err, cl::Buffer buffer_inImage(context, CL_MEM_READ_ONLY | CL_MEM_USE_HOST_PTR, image_size_bytes,
                                             inImage.data(), &err));
    OCL_CHECK(err, cl::Buffer buffer_outImage(context, CL_MEM_USE_HOST_PTR | CL_MEM_WRITE_ONLY, image_size_bytes,
                                              outImage.data(), &err));

    OCL_CHECK(err, err = kernel.setArg(0, buffer_inImage));
    OCL_CHECK(err, err = kernel.setArg(1, buffer_outImage));
    OCL_CHECK(err, err = kernel.setArg(2, width));
    OCL_CHECK(err, err = kernel.setArg(3, height));

    // Copy input Image to device global memory
    OCL_CHECK(err, err = q.enqueueMigrateMemObjects({buffer_inImage}, 0 /* 0 means from host*/));

    // Launch the Kernel
    OCL_CHECK(err, err = q.enqueueNDRangeKernel(kernel, 0, 1, 1, nullptr, nullptr));

    // Copy Result from Device Global Memory to Host Local Memory
    OCL_CHECK(err, err = q.enqueueMigrateMemObjects({buffer_outImage}, CL_MIGRATE_MEM_OBJECT_HOST));
    OCL_CHECK(err, err = q.finish());
    // OPENCL HOST CODE AREA END

    // Compare Golden Image with Output image
    bool match = 0;
    if (image.getHeight() != goldenImage.getHeight() || image.getWidth() != goldenImage.getWidth()) {
        match = 1;
    } else {
        int* goldImgPtr = goldenImage.bitmap();
        for (unsigned int i = 0; i < image.numPixels(); i++) {
            if (outImage[i] != goldImgPtr[i]) {
                match = 1;
                printf("Pixel %d Mismatch Output %x and Expected %x \n", i, outImage[i], goldImgPtr[i]);
                break;
            }
        }
    }

    // Write the final image to disk
    image.writeBitmapFile(outImage.data());

    std::cout << "TEST " << (match ? "FAILED" : "PASSED") << std::endl;
    return (match ? EXIT_FAILURE : EXIT_SUCCESS);
}
