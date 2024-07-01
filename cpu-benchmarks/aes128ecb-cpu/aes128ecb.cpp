#include <iostream>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/aes.h>
#include "util.h"

const unsigned char aes_key[16] = {0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c};

void func(std::string_view &input, std::stringstream &output) {

	const char* in = input.data();
	size_t bytes = input.size();

    unsigned char* cipher = new unsigned char[bytes+1024];
    int c_bytes;
    
	EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    EVP_EncryptInit_ex(ctx, EVP_aes_128_ecb(), NULL, aes_key, NULL);
	EVP_EncryptUpdate(ctx, cipher, &c_bytes, (unsigned char*)in, bytes);
	output.write((char*)cipher, c_bytes);
	EVP_EncryptFinal_ex(ctx, cipher, &c_bytes);
	output.write((char*)cipher, c_bytes);
	
	delete cipher;

}

