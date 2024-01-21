#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <errno.h>
#include <assert.h>
#include "hll.h"

int main(int argc, char** argv) {

    hll_t h;
    int ret;

    ret = hll_init(14, &h);
    assert(ret==0);

    int32_t value;
    char buf[8];
    while(scanf("%d", &value) != EOF) {
        uint32_t x = value;
        buf[0] = x&0xff;
        buf[1] = (x>>8)&0xff;
        buf[2] = (x>>16)&0xff;
        buf[3] = (x>>24)&0xff;
        buf[4] = 0;
        hll_add(&h, (char*)&buf);
    } 

    double s = hll_size(&h);
    printf("%.2f \n", s);


    hll_destroy(&h);

    return 0;
}
