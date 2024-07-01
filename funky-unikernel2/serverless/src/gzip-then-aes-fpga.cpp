#include "fpga-util.h"

const size_t AES_BLOCK_SIZE = 128;
uint64_t const keyLow = 0xabf7158809cf4f3c;
uint64_t const keyHigh = 0x2b7e151628aed2a6;

void func(std::string_view &input, std::stringstream &output) {
	size_t delimiter = input.find('\n');
	if(delimiter == input.npos) {
		output<<"Bad request: Missing delimiter"<<std::endl;
		return;
	}

	// with the current implementation, we need to know the output size in advance
	// as we have to pass Coyote the number of bytes to be written
	size_t gzip_output_size = atoi(input.data());
	if(gzip_output_size <= 0) {
		output<<"Bad request: Invalid output size"<<std::endl;
		return;
	}

	// calculate the size of the memory buffers
	size_t gzip_input_size = input.size()-delimiter-1;
	size_t aes_padding = AES_BLOCK_SIZE/8 - gzip_output_size % (AES_BLOCK_SIZE/8);
	size_t aes_padded_len = gzip_output_size + aes_padding;
	size_t alloc_size = std::max(gzip_input_size, aes_padded_len);

	std::cerr<<"Before alloc"<<std::endl;
	void* mem = h_alloc(alloc_size);

	// prepare gzip input data
	input.copy((char*)mem, gzip_input_size, delimiter+1);

	// invoke gzip
	std::cerr<<"Before gzip invocation"<<std::endl;
	solo5_serverless_map_memory(mem, alloc_size, gzip_input_size, gzip_output_size);
	solo5_serverless_load_bitstream(7);
	solo5_serverless_exec();

	// prepare aes input data
	std::memset((uint8_t*)mem+gzip_output_size, (uint8_t)aes_padding, aes_padding);
	bswap128(mem, aes_padded_len);

	// invoke aes
	std::cerr<<"Before aes invocation"<<std::endl;
	solo5_serverless_map_memory(mem, aes_padded_len, aes_padded_len, aes_padded_len);
	solo5_serverless_load_bitstream(1);
	solo5_serverless_set_csr(0, keyLow);
	solo5_serverless_set_csr(1, keyHigh);
	solo5_serverless_exec();

	bswap128(mem, aes_padded_len);
	output.write((char*)mem, aes_padded_len);

	h_free(mem, alloc_size);
}

