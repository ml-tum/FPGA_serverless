#pragma once

#ifdef NO_UNIKERNEL
#include "fpga-hypercall-mock.h"
#else
#include <os> // IncludeOS
extern "C" {
#include <solo5.h>
}
#endif

#include <stdlib.h>
#include <string>
#include <sstream>
//#include <chrono>
#include <iomanip>
#include <sys/mman.h>


typedef unsigned __int128 uint128_t;

template<class T>
T roundup(T n, T k) {
	return n%k==0 ? n : n+(k-n%k);
}

void* a_alloc(size_t bytes) {
	const size_t ALIGNMENT = 64;
	assert(bytes > 0);
	bytes = roundup(bytes, ALIGNMENT);
	void *ptr = aligned_alloc(ALIGNMENT, bytes);
	assert(ptr!=NULL);
	return ptr;
}

void a_free(void* ptr, size_t bytes) {
	free(ptr);
}

void* b_alloc(size_t bytes) {
	const size_t ALIGNMENT = 2*1024*1024;
	assert(bytes > 0);
	bytes = roundup(bytes, ALIGNMENT);
	void *ptr = mmap(NULL, bytes, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0);
	assert(ptr!=NULL);
	return ptr;
}

void b_free(void* ptr, size_t bytes) {
	const size_t ALIGNMENT = 2*1024*1024;
	bytes = roundup(bytes, ALIGNMENT);
	munmap(ptr, bytes);
}

void* h_alloc(size_t bytes) {
	return b_alloc(bytes);
}

void h_free(void* ptr, size_t bytes) {
	return b_free(ptr, bytes);
}

void bswap128(void *mem, int bytes) {
	assert(bytes%16==0);
	auto mem64 = (uint64_t*)mem;
	for(int i=0; i<bytes/8; i+=2) {
		mem64[i] = __builtin_bswap64(mem64[i]);
		mem64[i+1] = __builtin_bswap64(mem64[i+1]);
		std::swap(mem64[i], mem64[i+1]);
	}
}

long long int getMillis() {
	timespec ts;
    long long int millis;
	clock_gettime(CLOCK_REALTIME, &ts);
    millis = ts.tv_sec*1000LL + ts.tv_nsec/1000LL/1000LL;
    return millis;
}
