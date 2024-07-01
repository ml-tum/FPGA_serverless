#include "fpga-util.h"
#include <sys/mman.h>

using namespace std;

const int VALUES_PER_SAMPLE = 32*32*3;
const int BYTES_PER_SAMPLE = VALUES_PER_SAMPLE*2;
const int BYTES_PER_RESULT = 64;

void func(std::string_view &input, std::stringstream &output) {

	size_t delimiter = input.find('\n');
	if(delimiter == input.npos) {
		output<<"Bad request: Missing delimiter"<<endl;
		return;
	}

	int samples_count = atoi(input.data());
	if(samples_count <= 1) {
		output<<"Bad request: Samples count = "<<samples_count<<endl;
		return;
	}

	const size_t payload_size = input.size()-delimiter-1;
	if(payload_size != samples_count*VALUES_PER_SAMPLE) {
		output<<"Bad request: Mismatch between number of samples ("<<samples_count<<") and payload size ("<<payload_size<<")."<<endl;
		return;
	}

	const size_t alloc_size = roundup(samples_count*BYTES_PER_SAMPLE, 4096);
	void* mem = h_alloc(alloc_size);
	uint16_t* smem = (uint16_t*)mem;

	for(int i=0; i<samples_count; i++) {
		uint8_t *src = (uint8_t*)input.data()+delimiter+1+i*VALUES_PER_SAMPLE;
		uint16_t *dst = smem+i*VALUES_PER_SAMPLE;
	    for(int j=0; j<32*32*3; j++) {
	    	//is channel order relevant?
	    	//smem[j] = image[j]/255.0*(1<<10)+0.5; //convert to fixed point 
			assert(src+j < (uint8_t*)input.data()+input.size());
			assert((uint8_t*)(dst+j) < (uint8_t*)mem+alloc_size);
	    	dst[j] = src[j]/255.0*(1<<10)+0.5;
	    }
	}

	assert(alloc_size >= samples_count*BYTES_PER_SAMPLE);
	solo5_serverless_load_bitstream(5);
	solo5_serverless_map_memory(mem, alloc_size, samples_count*BYTES_PER_SAMPLE, samples_count*BYTES_PER_RESULT);
	solo5_serverless_exec();

    for(int i=0; i<samples_count; i++) {
        uint16_t maxarg=-1;
        float maxval=-1;
        for(int j=0; j<10; j++) {
            uint16_t fixp = smem[i*BYTES_PER_RESULT/2+j];
            float fpv = ((float)fixp)/(1<<10);
            if(fpv > maxval) {
                maxarg = j;
                maxval = fpv;
            }
        }
        output<<"Result: "<<maxarg<<", Score: "<<maxval<<endl;
    }

	h_free(mem, alloc_size);
}
