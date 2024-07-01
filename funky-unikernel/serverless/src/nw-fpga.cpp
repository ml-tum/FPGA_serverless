#include "fpga-util.h"

using namespace std;

void func(std::string_view &input, std::stringstream &output) {
	
	size_t delimiter = input.find('\n');
	if(delimiter == input.npos) {
		output<<"Bad request: Invalid format"<<endl;
		return;
	}

	stringstream stst;
	stst<<input.substr(0, delimiter);

	uint16_t s0_words, s1_words;
	string s0, s1;
	if(!(stst>>s0_words>>s1_words)) {
		output<<"Bad request: Invalid format"<<endl;
		return;
	}

	// Not sure, if this is strictly necessary
	if(__builtin_popcount(s0_words)!=1 || __builtin_popcount(s1_words)!=1) {
		output<<"Bad request: Not power of 2 lengths"<<endl;
		return;
	}

	const int bytes_per_word = 64;
	int binary_bytes = ((int)input.size())-delimiter-1;

	if(binary_bytes < s0_words*bytes_per_word + s1_words*bytes_per_word) {
		output<<"Bad request: Binary section only "<<binary_bytes<<" bytes long"<<endl;
		return;
	}


	
	const uint64_t s_ratio = 512/128;
    const uint64_t sc_ratio = 512/8;
    const uint64_t sc_count = s0_words*s_ratio * s1_words*s_ratio;
    const uint64_t sc_words = (sc_count+sc_ratio-1)/sc_ratio;

	const int meta_size = 64;
	const int input_size = meta_size + s0_words*bytes_per_word + s1_words*bytes_per_word;
	const int output_size = sc_words*64;
	const int alloc_size = max(input_size, output_size);
	void* mem = h_alloc(alloc_size);

	((uint64_t*)mem)[0] = s0_words;
    ((uint64_t*)mem)[1] = s1_words;
    ((uint64_t*)mem)[2] = sc_count;
    ((uint64_t*)mem)[3] = sc_words;
	memcpy((char*)mem+meta_size, input.data()+delimiter+1, input_size);

	solo5_serverless_map_memory(mem, alloc_size, input_size, output_size);
    solo5_serverless_load_bitstream(4);
    solo5_serverless_exec();


	for(int i=0; i<(int)sc_count; i++) {
		char space = (i+1)%(s1_words*s_ratio) == 0 ? '\n' : ' ';
		output<<(int)((int8_t*)mem)[i]<<space;
	}


	h_free(mem, alloc_size);
}
