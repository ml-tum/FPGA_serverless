#include "fpga-util.h"

using namespace std;

void func(std::string_view &input, std::stringstream &output) {

	stringstream stst;
	stst<<input;

	vector<int32_t> vec;
	int32_t value;
	while(stst>>value) {
		vec.push_back(value);
	}

	if(vec.empty()) {
		output<<"0"<<endl;
		return;
	}

	int alloc_size = vec.size() * sizeof(int32_t);
	void* mem = h_alloc(alloc_size);

	for(int i=0; i<vec.size(); i++) {
		((int32_t*)mem)[i] = vec[i];
	}

    solo5_serverless_map_memory(mem, alloc_size, alloc_size, sizeof(int32_t));
    solo5_serverless_load_bitstream(8);
	solo5_serverless_exec();

	output<<*(float*)mem<<endl;
	
	h_free(mem, alloc_size);
}
