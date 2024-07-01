#include "fpga-util.h"

using namespace std;

void func(std::string_view &input, std::stringstream &output) {

	stringstream stst;
	stst<<input;

	const int MAT_BYTES = 64*64*sizeof(int64_t);	
	void* mem = a_alloc(3*MAT_BYTES);

	for(int i=0; i<2*64*64; i++) {
		int64_t val=0;
		stst>>val;
		((int64_t*)mem)[i] = val;
	}


	int64_t* ma = (int64_t*)mem;
	int64_t* mb = ma + 64*64;
	int64_t* mc = mb + 64*64;

	for(int i=0; i<64; i++) {
		for(int j=0; j<64; j++) {
			int64_t sum = 0;
			for(int k=0; k<64; k++) {
				//sum += ma[i][k] * mb[k][j];
				sum += *(ma+i*64+k) * *(mb+k*64+j);
			}
			*(mc+i*64+j) = sum;
		}
	}

	for(int i=0; i<64; i++) {
		for(int j=0; j<64; j++) {
			char space = j%64==63 ? '\n' : ' ';
			output<<*(mc+i*64+j)<<space;
		}
	}

	free(mem);
}
