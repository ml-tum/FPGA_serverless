#include "fpga-util.h"

using namespace std;

const int N = 32768;
using DT = float;

void func(std::string_view &input, std::stringstream &output) {

	int frames = input.size()/N/sizeof(DT);
	
	if(input.size()%(N*sizeof(DT)) != 0) {
		output<<"Bad request: Incomplete frame"<<endl;
		return;
	}
	if(frames==0) {
		output<<"Bad request: Empty request"<<endl;
		return;
	}

	uint64_t alloc_size = frames*N*sizeof(DT);
	void* mem = h_alloc(alloc_size);

	input.copy((char*)mem, input.size());

	solo5_serverless_map_memory(mem, alloc_size, alloc_size, alloc_size);
	solo5_serverless_load_bitstream(11);
	solo5_serverless_exec();

	output.write((char*)mem, alloc_size);

	h_free(mem, alloc_size);
}
