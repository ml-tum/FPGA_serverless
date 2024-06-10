#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <errno.h>
#include <assert.h>
#include "hll.h"
#include "../util/util.h"

#define BUFSIZE (64*1024*1024)
char buf[BUFSIZE];

int main(int argc, char** argv) {

    hll_t h;
    int ret;

    ret = hll_init(14, &h);
    assert(ret==0);

    int32_t value, count=0;
    char* ptr = buf;
    while(scanf("%d", &value) != EOF) {
        assert(ptr+5 < buf+BUFSIZE);
        uint32_t x = value;
        *(ptr++) = x&0xff;
        *(ptr++) = (x>>8)&0xff;
        *(ptr++) = (x>>16)&0xff;
        *(ptr++) = (x>>24)&0xff;
        *(ptr++) = 0;
        count++;
    }

    measure_start();
    for(int i=0; i<count; i++) {
        hll_add(&h, buf+(i*5));
    }
    double s = hll_size(&h);
    measure_end();
    measure_write("hyperloglog", "cpu", count*sizeof(uint32_t));

    printf("%.2f \n", s);

    hll_destroy(&h);

    return 0;
}