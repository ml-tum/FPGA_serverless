#include <iostream>
#include "../util/util.h"

using namespace std;

int64_t ma[64][64];
int64_t mb[64][64];
int64_t mc[64][64];

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

        measure_start();
        for(int r=0; r<64; r++) {
                for(int c=0; c<64; c++) {
                        mc[r][c]=0;
                        for(int k=0; k<64; k++) {
                                mc[r][c] += ma[r][k]*mb[k][c];
                        }
                }
        }
        measure_end();
        measure_write("matmul", "cpu", 64*64*2*sizeof(int64_t));

        for(int r=0; r<64; r++) {
                for(int c=0; c<64; c++) {
                        char space = c==63 ? '\n' : ' ';
                        cout<<mc[r][c]<<space;
                }
        }

	return 0;
}
