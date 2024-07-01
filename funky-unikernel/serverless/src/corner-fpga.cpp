#pragma GCC optimize("O3")

#include "fpga-util.h"

#define STB_IMAGE_IMPLEMENTATION
#define STBI_NO_STDIO
#define STBI_ONLY_JPEG
#define STBI_NO_SIMD
#define STBI_NO_THREAD_LOCALS
#define STBI_NO_LINEAR
#define STBI_NO_HDR
#define STB_IMAGE_STATIC
#include "stb_image.h"

using namespace std;

void func(std::string_view &input, std::stringstream &output) {

    printf("#start %lld \n", getMillis());

    int width = -1, height = -1, type = -1;
    unsigned char* image = nullptr;

    image = stbi_load_from_memory((const unsigned char*)input.data(), (int)input.size(), &width, &height, &type, 0);
    printf("#after stbi load %lld \n", getMillis());

    output<<"Dimensions "<<height<<" "<<width<<" "<<type<<endl;

    if(image==nullptr) {
        output<<"Bad Request: Not a valid image"<<endl;
        return;
    }
    if(height != 1080 || width != 1920 || type != STBI_grey) {
        stbi_image_free(image);
        output<<"Bad Request: Wrong dimensions, "<<height<<", "<<width<<", "<<type<<endl;
        return;
    }


    const int alloc_size = 1920*1080;
    void* mem = h_alloc(alloc_size);
    memcpy(mem, image, alloc_size);

    solo5_serverless_map_memory(mem, alloc_size, alloc_size, alloc_size);
    solo5_serverless_load_bitstream(9);
    solo5_serverless_exec();



    for (int r = 0; r < height; r++) {
        for (int c = 0; c < width; c++) {
            if (((uint8_t*)mem)[r*1920+c] >= 255) {
                output<<r<<" "<<c<<endl;
            }
        }
    }


    stbi_image_free(image);
    h_free(mem, alloc_size);
}

