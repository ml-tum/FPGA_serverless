#include "fpga-util.h"

using namespace std;

void func(std::string_view &input, std::stringstream &output) {

	size_t delimiter = input.find('\n');
	if(delimiter == input.npos) {
		output<<"Bad request: Missing delimiter"<<endl;
		return;
	}

	// with the current implementation, we need to know the output size in advance
	// as we have to pass Coyote the number of bytes to be written
	uint64_t output_size = atoi(input.data());
	if(output_size <= 0) {
		output<<"Bad request: Invalid output size"<<endl;
		return;
	}

	uint64_t payload_size = input.size()-delimiter-1;
	uint64_t alloc_size = max(payload_size, output_size);
	void* mem = h_alloc(alloc_size);

	input.copy((char*)mem, payload_size, delimiter+1);

	solo5_serverless_map_memory(mem, alloc_size, payload_size, output_size);
	solo5_serverless_load_bitstream(7);
	solo5_serverless_exec();

	output.write((char*)mem, output_size);


	h_free(mem, alloc_size);
}
