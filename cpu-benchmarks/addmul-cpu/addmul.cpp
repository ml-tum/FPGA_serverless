#include <iostream>
#include <vector>
#include "../util/util.h"

using namespace std;

int main() {
	vector<uint32_t> vec;
	uint32_t val;
	while(cin>>val) {
		vec.push_back(val);
	}

	if(vec.size() <= 2) {
		cout<<"Bad request"<<endl;
		return 1;
	}

	uint32_t mul = vec[0];
	uint32_t add = vec[1];
	measure_start();
	for(size_t i=2; i<vec.size(); i++) {
		vec[i] = ((vec[i]<<mul)+add);
	}
	measure_end();
	
	for(size_t i=2; i<vec.size(); i++) {
		cout<<vec[i]<<endl;
	}
	
	measure_write("addmul", "cpu", (-2+(int)vec.size())*sizeof(uint32_t));

	return 0;
}
