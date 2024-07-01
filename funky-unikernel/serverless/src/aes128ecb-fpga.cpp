#include "fpga-util.h"

const size_t AES_BLOCK_SIZE = 128;
uint64_t const keyLow = 0xabf7158809cf4f3c;
uint64_t const keyHigh = 0x2b7e151628aed2a6;
uint64_t const plainLow = 0xe93d7e117393172a;
uint64_t const plainHigh = 0x6bc1bee22e409f96;


void func(std::string_view &input, std::stringstream &output) {

	size_t pt_len = input.size();
	size_t padding = AES_BLOCK_SIZE/8 - pt_len % (AES_BLOCK_SIZE/8);
	size_t pt_padded_len = pt_len + padding;

	std::cerr<<"Before alloc"<<std::endl;
	void *mem = h_alloc(pt_padded_len);

	std::cerr<<"Before memcpy"<<std::endl;
	std::memcpy(mem, input.data(), pt_len);
	std::memset((uint8_t*)mem+pt_len, (uint8_t)padding, pt_padded_len-pt_len);
	bswap128(mem, pt_padded_len);


	std::cerr<<"Before prepare_aes"<<std::endl;
    solo5_serverless_map_memory(mem, pt_padded_len, pt_padded_len, pt_padded_len);
    solo5_serverless_load_bitstream(1);
    solo5_serverless_set_csr(0, keyLow);
    solo5_serverless_set_csr(1, keyHigh);
	solo5_serverless_exec();


	std::cerr<<"After exec"<<std::endl;
	bswap128(mem, pt_padded_len);
	//for(size_t i=0; i<pt_padded_len; i++) {
	//	output<<std::setw(2)<<std::setfill('0')<<std::hex<<(int)((uint8_t*)mem)[i];
	//}
	//output<<std::endl;
	output.write((char*)mem, pt_padded_len);
	
	h_free(mem, pt_padded_len);
}
