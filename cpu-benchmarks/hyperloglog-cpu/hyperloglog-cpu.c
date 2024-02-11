#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <errno.h>
#include <assert.h>
#include "hll.h"
#include "../util/util.h"

int main(int argc, char** argv) {

    hll_t h;
    int ret;

    ret = hll_init(14, &h);
    assert(ret==0);

    int32_t value, count=0;
    char buf[8];
    while(scanf("%d", &value) != EOF) {
        count++;
        measure_start();
        uint32_t x = value;
        buf[0] = x&0xff;
        buf[1] = (x>>8)&0xff;
        buf[2] = (x>>16)&0xff;
        buf[3] = (x>>24)&0xff;
        buf[4] = 0;
        hll_add(&h, (char*)&buf);
        measure_end();
    }

    measure_start();
    double s = hll_size(&h);
    measure_end();
    measure_write("hyperloglog", "cpu", count*sizeof(uint32_t));

    printf("%.2f \n", s);

    hll_destroy(&h);

    return 0;
}
