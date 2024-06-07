#include <iostream>
#include <iomanip>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/md5.h>
#include "util.h"

const int WORDLEN = 5;
const int HASHLEN = 16;
const int MAX_ITERATIONS = 1073741824; //64^5
char word[WORDLEN+1] = {0,0,0,0,0,0};
unsigned char hash[HASHLEN+1];

void compute_md5() {
	unsigned int c_bytes;
	EVP_MD_CTX* context = EVP_MD_CTX_new();
	EVP_DigestInit_ex(context, EVP_md5(), nullptr);
	EVP_DigestUpdate(context, word, WORDLEN);
	EVP_DigestFinal_ex(context, hash, &c_bytes);
}

void compute_word(int ctr) {
	for(int i=0; i<WORDLEN; i++) {
        int v = ctr % 64;
        ctr /= 64;

        char c;
        if (v<=9) c = '0'+v;
        else if (v<=35) c = 'A'+(v-10);
        else if (v<=61) c = 'a'+(v-36);
        else if (v==62) c = '-';
        else c = '_';
        word[WORDLEN-1-i] = c;
    }
}

int main() {

	std::string input;
	std::cin>>input;
	assert(input.size()==HASHLEN*2); //hexadecimal

	char needle[HASHLEN];
	for(int i=0; i<HASHLEN; i++) {
		char byt[3];
        byt[0] = input[2*i];
        byt[1] = input[2*i+1];
        byt[2] = '\0';
		needle[i] = strtol(byt, NULL, 16);
	}


	int ctr = 0;

	measure_start();
	for(int c=0; c<MAX_ITERATIONS; c++) {
		compute_word(c);
		compute_md5();
		//hash[32]=0;
		//printf("%s\n", hash);
		if(strncmp((char*)hash, needle, WORDLEN)==0) {
			break;
		}
	}	
	measure_end();

	printf("Result: %s\n", word);
    
	measure_write("md5", "cpu", WORDLEN);

	return 0;
}
