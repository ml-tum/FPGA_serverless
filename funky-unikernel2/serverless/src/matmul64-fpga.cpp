#include "fpga-util.h"

using namespace std;

void func(std::string_view &input, std::stringstream &output) {

	stringstream stst;
	stst<<input;

	const int MAT_BYTES = 64*64*sizeof(int64_t);
	void* mem = h_alloc(2*MAT_BYTES);

	for(int i=0; i<2*64*64; i++) {
		int64_t val=0;
		stst>>val;
		((int64_t*)mem)[i] = val;
	}

	solo5_serverless_map_memory(mem, 2*MAT_BYTES, 2*MAT_BYTES, MAT_BYTES);
	solo5_serverless_load_bitstream(6);
	solo5_serverless_exec();

	for(int i=0; i<64*64; i++) {
		char space = i%64==63 ? '\n' : ' ';
		output<<((int64_t*)mem)[i]<<space;
	}

	h_free(mem, 2*MAT_BYTES);
}
