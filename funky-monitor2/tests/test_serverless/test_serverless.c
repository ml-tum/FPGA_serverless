#include "solo5.h"
#include "../../kernel/lib.c"

#define NANOPRINTF_IMPLEMENTATION
#include "nanoprintf.h"

static void puts(const char *s)
{
    solo5_console_write(s, strlen(s));
}


#define SIZE 4096
#define ALIGNMENT 64
char memUnaligned[SIZE+ALIGNMENT];

char printf_buf[2048];
int printf(char const *fmt, ...) {
    va_list val;
    va_start(val, fmt);
    int const rv = npf_vsnprintf(printf_buf, sizeof printf_buf, fmt, val);
    va_end(val);
    puts(printf_buf);
    return rv;
}

void prepare_addmul(void *mem, int bytes) {
    const int add=5;
    const int mul=2;

    for(int i=0; i<(int)(bytes/sizeof(uint32_t)); i++) {
        ((uint32_t*)mem)[i]=i;
    }

    solo5_serverless_map_memory(mem, bytes, bytes, bytes);
    solo5_serverless_load_bitstream(0);
    solo5_serverless_set_csr(0, mul);
    solo5_serverless_set_csr(1, add);
}

void check_addmul(void *mem, int bytes)
{
    const int add=5;
    const int mul=2;
    bool correct=true;

    for(int i=0; i<(int)(bytes/sizeof(uint32_t)); i++) {
        correct &= ((uint32_t*)mem)[i] == (((uint32_t)i)<<mul)+add;
    }

    printf("Check AddMul: result is %s\n", correct ? "correct :)" : "wrong !!");
}

void prepare_aes(void *mem, int bytes)
{

    uint64_t const keyLow = 0xabf7158809cf4f3c;
    uint64_t const keyHigh = 0x2b7e151628aed2a6;
    uint64_t const plainLow = 0xe93d7e117393172a;
    uint64_t const plainHigh = 0x6bc1bee22e409f96;

    solo5_serverless_map_memory(mem, bytes, bytes, bytes);
    solo5_serverless_load_bitstream(0);
    solo5_serverless_set_csr(0, keyLow);
    solo5_serverless_set_csr(1, keyHigh);

    for(int i=0; i<(int)(bytes/sizeof(uint64_t)); i++) {
        ((uint64_t*)mem)[i]= i%2?plainHigh:plainLow;
    }
}

void check_aes(void *mem, int bytes)
{
    uint64_t const cipherLow = 0xa89ecaf32466ef97;
    uint64_t const cipherHigh = 0x3ad77bb40d7a3660;
    bool correct=true;

    for(int i=0; i<(int)(bytes/sizeof(uint64_t)); i++) {
        correct &= ((uint64_t*)mem)[i] == (i%2?cipherHigh:cipherLow);
    }

    printf("Check AES: result is %s\n", correct ? "correct :)" : "wrong !!");
}


int solo5_app_main(const struct solo5_start_info *si)
{
    (void)si; //suppress "unused variable" error

    puts("\n**** Solo5 standalone test_serverless ****\n\n");


    void *mem = memUnaligned + ALIGNMENT - ((int64_t)memUnaligned)%ALIGNMENT;



    // hello FPGA 
    puts("guest  : calling a hypercall...\n");
    solo5_time_t start = solo5_clock_wall();
    prepare_aes(mem, SIZE);
    solo5_serverless_exec();
    check_aes(mem, SIZE);
    solo5_time_t end = solo5_clock_wall();
    uint64_t nanos = end-start;
    puts("guest  : hypercall is finished.\n");
    printf("duration: %d,%03d ms \n", nanos/1000000, nanos/1000%1000);

    /*solo5_time_t start = solo5_clock_wall();
    solo5_time_t second = 1000*1000*1000;
    while(solo5_clock_wall() - start < 5*second) {
    }*/

    puts("results: ");
    for(int i=0; i<16; i++) {
        uint64_t val = ((uint64_t*)mem)[i];
        printf("%s 0x%x", (i==0 ? "" : ","), val);
    }
    puts(" ...\n");

    /*while(solo5_clock_wall() - start < 1L*1000*1000*180) {
    	;
    }*/

    return SOLO5_EXIT_SUCCESS;
}
