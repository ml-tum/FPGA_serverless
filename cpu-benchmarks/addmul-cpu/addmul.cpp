#include <iostream>
#include <vector>
#include "util.h"

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

	uint32_t mul = vec[0];
	uint32_t add = vec[1];

	for(int i=0; i<ints; i++) {
		output<<((vec[i+2]<<mul)+add)<<endl;
	}
}
