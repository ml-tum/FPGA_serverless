#include "fpga-util.h"

void func(std::string_view &input, std::stringstream &output) {

	size_t input_size = input.size();
	size_t input_size_padded = roundup(input_size+1+8, (size_t)64);
	
	size_t alloc_size = input_size_padded;
	void* mem = h_alloc(alloc_size);

	memcpy(mem, input.data(), input_size);
	memset(((uint8_t*)mem)+input_size, 0x00, input_size_padded-input_size);

	((uint8_t*)mem)[input_size] = 0x80;
	((uint64_t*)mem)[input_size_padded/8-1] = __builtin_bswap64(input_size*8);

	assert(input_size_padded > 0);
	solo5_serverless_map_memory(mem, alloc_size, input_size_padded, 32);
	solo5_serverless_load_bitstream(3);
	solo5_serverless_exec();

	for(int i=0; i<32; i++) {
		output<<std::setw(2)<<std::setfill('0')<<std::hex<<(int)((uint8_t*)mem)[31-i];
	}
	output<<std::endl;


	h_free(mem, alloc_size);
}
