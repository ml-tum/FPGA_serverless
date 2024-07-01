#include "fpga-util.h"

const int LEN = 5;

void func(std::string_view &input, std::stringstream &output) {

    assert(input.size()>=32); //hex input

    size_t alloc_size = 64;
    void* mem = h_alloc(alloc_size);
    memset(mem, 0, 64);

    for(int i=0; i<16; i++) {
        char byt[3];
        byt[0] = input[2*i];
        byt[1] = input[2*i+1];
        byt[2] = '\0';
        ((uint8_t*)mem)[15-i] = strtol(byt, NULL, 16);
    }

    solo5_serverless_map_memory(mem, alloc_size, alloc_size, alloc_size);
    solo5_serverless_load_bitstream(10);
    solo5_serverless_exec();


    uint64_t ctr = ((uint64_t*)mem)[0];
    char result[LEN+1] = "*****";
    for(int i=0; i<LEN; i++) {
        int v = ctr % 64;
        ctr /= 64;

        char c;
        if (v<=9) c = '0'+v;
        else if (v<=35) c = 'A'+(v-10);
        else if (v<=61) c = 'a'+(v-36);
        else if (v==62) c = '-';
        else c = '_';
        result[LEN-1-i] = c;
    }

    output<<result<<std::endl;

    h_free(mem, alloc_size);
}
