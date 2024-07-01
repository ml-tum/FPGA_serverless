#include "fpga-util.h"

void func(std::string_view &input, std::stringstream &output) {

	printf("#Alloc, %lld\n", getMillis());
	size_t input_size = input.size();
	if(input_size==0) {
		output<<"Bad request: Input is empty"<<std::endl;
		return;
	}

	size_t alloc_size = std::max(input_size, (size_t)64);
	void* mem = h_alloc(alloc_size);
	
	printf("#Memcpy, %lld\n", getMillis());
	memcpy(mem, input.data(), input_size);

	printf("#hypercalls 1, %lld\n", getMillis());
	solo5_serverless_map_memory(mem, alloc_size, input_size, 64);
	printf("#hypercalls 2, %lld\n", getMillis());
	solo5_serverless_load_bitstream(0);
	printf("#hypercalls 3, %lld\n", getMillis());
	solo5_serverless_exec();

	printf("#print result, %lld\n", getMillis());
	for(int i=0; i<8; i++) {
		output<<std::setw(16)<<std::setfill('0')<<std::hex<<((uint64_t*)mem)[7-i];
	}
	output<<std::endl;

	h_free(mem, alloc_size);
}
