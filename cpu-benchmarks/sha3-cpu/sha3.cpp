#include <iostream>
#include <iomanip>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/sha.h>
#include "util.h"

const int bufsize = 1024*1024;
const int hashsize = 64;
unsigned char buf[bufsize];
unsigned char hash[hashsize];

int main() {
	EVP_MD_CTX* context = EVP_MD_CTX_new();
	EVP_DigestInit_ex(context, EVP_sha3_512(), nullptr);

    	size_t totalbytes=0;
    	uint32_t c_bytes;

	while(true) {
		std::cin.read((char*)buf, bufsize);
		size_t bytes = std::cin.gcount();
		if(bytes <= 0)
			break;
		totalbytes += bytes;

		measure_start();
		EVP_DigestUpdate(context, buf, bytes);
		measure_end();
	}

	measure_start();
	EVP_DigestFinal_ex(context, hash, &c_bytes);
	measure_end();

	for(int i = 0; i < hashsize; i++)
	{
		std::cout << std::hex << std::setw(2) << std::setfill('0') << (uint16_t)hash[i];
	}
	std::cout << std::endl;
        
	measure_write("sha3", "cpu", totalbytes);

	return 0;
}

