#include <iostream>
#include <vector>
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
	for(size_t i=2; i<vec.size(); i++) {
		cout<<((vec[i]<<mul)+add)<<endl;
	}

	return 0;
}
