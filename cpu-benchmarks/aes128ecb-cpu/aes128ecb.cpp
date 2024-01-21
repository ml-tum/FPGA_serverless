#include <iostream>
#include <openssl/evp.h>
#include <openssl/aes.h>

//const unsigned char aes_key[16] = {0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c, 0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6};
const unsigned char aes_key[16] = {0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c};

int encrypt_aes_ecb(const unsigned char *plaintext, int plaintext_len,
                    const unsigned char *key, unsigned char *ciphertext)
{
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (ctx == NULL)
    {
        std::cout << "Error: EVP_CIPHER_CTX_new" << std::endl;
        return -1;
    }

    int err = EVP_EncryptInit_ex(ctx, EVP_aes_128_ecb(), NULL, key, NULL);
    if (err != 1)
    {
        EVP_CIPHER_CTX_free(ctx);
        std::cout << "Error: EVP_EncryptInit_ex" << std::endl;
        return err;
    }

    err = EVP_EncryptUpdate(ctx, ciphertext, &plaintext_len, plaintext, plaintext_len);
    if (err != 1)
    {
        std::cout << "Error: EVP_EncryptUpdate" << std::endl;
        EVP_CIPHER_CTX_free(ctx);
        return err;
    }

    err = EVP_EncryptFinal_ex(ctx, ciphertext + plaintext_len, &plaintext_len);
    if (err != 1)
    {
        std::cout << "Error: EVP_EncryptFinal_ex" << std::endl;
        EVP_CIPHER_CTX_free(ctx);
        return err;
    }

    EVP_CIPHER_CTX_free(ctx);

    return plaintext_len;
}

const int bufsize = 1024*1024;
char buf[bufsize];
char cipher[bufsize];

int main() {
	while(true) {
		std::cin.read(buf, bufsize);
		size_t bytes = std::cin.gcount();
		if(bytes <= 0)
			break;
		encrypt_aes_ecb((unsigned char*)buf, bytes, aes_key, (unsigned char*)cipher);
		std::cout.write(cipher, bytes);
	}
	return 0;
}

