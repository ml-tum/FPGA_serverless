#include <iostream>
#include "util.h"

using namespace std;

int64_t ma[64][64];
int64_t mb[64][64];
int64_t mc[64][64];

void func(std::string_view &input, std::stringstream &output) {

    stringstream stst;
    stst<<input;

	for(int r=0; r<64; r++) {
		for(int c=0; c<64; c++) {
			stst>>ma[r][c];
		}
	}
	for(int r=0; r<64; r++) {
		for(int c=0; c<64; c++) {
			stst>>mb[r][c];
		}
	}

    for(int r=0; r<64; r++) {
        for(int c=0; c<64; c++) {
            mc[r][c]=0;
            for(int k=0; k<64; k++) {
                    mc[r][c] += ma[r][k]*mb[k][c];
                }
        }
    }

    for(int r=0; r<64; r++) {
        for(int c=0; c<64; c++) {
            char space = c==63 ? '\n' : ' ';
            cout<<mc[r][c]<<space;
        }
    }
}
