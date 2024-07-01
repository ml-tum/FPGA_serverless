#include <iostream>
#include <iomanip>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/sha.h>
#include "util.h"

const int hashsize = 32;
unsigned char hash[hashsize];

void func(std::string_view &input, std::stringstream &output) {
	
	const char* in = input.data();
	size_t bytes = input.size();

	EVP_MD_CTX* context = EVP_MD_CTX_new();
	EVP_DigestInit_ex(context, EVP_sha256(), nullptr);
	EVP_DigestUpdate(context, (unsigned char*)in, bytes);
	
	uint32_t c_bytes;
	EVP_DigestFinal_ex(context, hash, &c_bytes);

	for(int i = 0; i < hashsize; i++) {
		std::cout << std::hex << std::setw(2) << std::setfill('0') << (uint16_t)hash[i];
	}
	std::cout << std::endl;
}

