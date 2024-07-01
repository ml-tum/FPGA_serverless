#include "fpga-util.h"

using namespace std;

void func(std::string_view &input, std::stringstream &output) {

	vector<uint32_t> vec;
	stringstream stst;
	stst<<input;

	int32_t val;
	while(stst>>val) {
		vec.push_back(val);
	}


	int ints = -2+(int)vec.size();
	if(ints <= 0) {
		output<<"Bad request"<<endl;
		return;
	}

	int alloc_size = ints*sizeof(int32_t);
	void* mem = h_alloc(alloc_size);
	for(int i=0; i<ints; i++) {
		((uint32_t*)mem)[i] = vec[i+2];
	}

	solo5_serverless_set_csr(0, vec[0]);
	solo5_serverless_set_csr(1, vec[1]);
	solo5_serverless_map_memory(mem, alloc_size, alloc_size, alloc_size);
	solo5_serverless_load_bitstream(2);
	solo5_serverless_exec();

	for(int i=0; i<ints; i++) {
		output<<((uint32_t*)mem)[i]<<endl;
	}

	h_free(mem, alloc_size);
}
