#include <iostream>

using namespace std;

int64_t ma[64][64];
int64_t mb[64][64];

int main() {

	for(int r=0; r<64; r++) {
		for(int c=0; c<64; c++) {
			cin>>ma[r][c];
		}
	}
	for(int r=0; r<64; r++) {
		for(int c=0; c<64; c++) {
			cin>>mb[r][c];
		}
	}
	for(int r=0; r<64; r++) {
		for(int c=0; c<64; c++) {
			int64_t cell=0;
			for(int k=0; k<64; k++) {
				cell += ma[r][k]*mb[k][c];
			}

			char space = c==63 ? '\n' : ' ';
			cout<<cell<<space;
		}
	}

	return 0;
}
