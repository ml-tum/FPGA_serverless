#include <iostream>
#include <thread>
#include <sstream>
#include <array>
#include "util.h"
using namespace std;

using uint128_t = unsigned __int128;

tuple<uint8_t,uint8_t,uint8_t,uint8_t> convert_byte(uint8_t b) {
    return { b&3, (b>>2)&3, (b>>4)&3, (b>>6)&3 };
}

template<size_t SIZE>
int needleman_wunsch(array<char,SIZE> a, array<char,SIZE> b) {

	int dp[SIZE+1][SIZE+1];
	for(int i=0; i<SIZE+1; i++) {
		dp[0][i] = -i;
        dp[i][0] = -i;
	}

	for(int i=0; i<SIZE; i++) {
		for(int j=0; j<SIZE; j++) {
			int match = a[i]==b[j] ? 1 : -1;
            dp[i+1][j+1] = max(max(dp[i][j+1]-1, dp[i+1][j]-1), dp[i][j]+match);
		}
	}

    return dp[SIZE][SIZE];
}

void func(std::string_view &input, std::stringstream &output)
{
	size_t delimiter = input.find('\n');
	if(delimiter == input.npos) {
		cout<<"Bad request: Invalid format"<<endl;
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


	uint8_t *s0_binary = (uint8_t*)(input.data()+delimiter+1);
	uint8_t *s1_binary = (uint8_t*)(s0_binary+s0_words*64);

	for(int i=0; i<s0_words*4; i++) {
		for(int j=0; j<s1_words*4; j++) {

			array<char,64> s0;
    		array<char,64> s1;
			for(int k=0; k<16; k++) {
				tie(s0[k*4],s0[k*4+1],s0[k*4+2],s0[k*4+3]) = convert_byte(*(s0_binary+i*16+k));
				tie(s1[k*4],s1[k*4+1],s1[k*4+2],s1[k*4+3]) = convert_byte(*(s1_binary+j*16+k));
    		}
			int score = needleman_wunsch(s0, s1);
			char space = j<s1_words*4-1 ? ' ' : '\n';
    		output<<score<<space;
		}
	}
}
