#include <iostream>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/aes.h>
#include "util.h"


const unsigned char aes_key[16] = {0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c};

const int bufsize = 1024*1024;
unsigned char buf[bufsize];
unsigned char cipher[bufsize];



int main() {
	EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    	EVP_EncryptInit_ex(ctx, EVP_aes_128_ecb(), NULL, aes_key, NULL);

	timespec start, end;
	long long int nanos=0;
    	size_t totalbytes=0;
    	int c_bytes;

	while(true) {
		std::cin.read((char*)buf, bufsize);
		size_t bytes = std::cin.gcount();
		if(bytes <= 0)
			break;
		totalbytes += bytes;

		measure_start();
		EVP_EncryptUpdate(ctx, cipher, &c_bytes, buf, bytes);
		measure_end();

		std::cout.write((char*)cipher, c_bytes);
	}

	measure_start();
	EVP_EncryptFinal_ex(ctx, cipher, &c_bytes);
	measure_end();

	std::cout.write((char*)cipher, c_bytes);

	measure_write("aes128ecb", "cpu", totalbytes);

	return 0;
}

