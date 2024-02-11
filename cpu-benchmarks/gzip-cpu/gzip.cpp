#include <iostream>
#include <zlib.h>
#include "../util/util.h"

const int bufsize = 1024*1024;
unsigned char buf[bufsize];
unsigned char out[bufsize];

#define windowBits 15
#define USE_GZIP 16
#define DEFAULT_MEMLEVEL 8
#define COMPRESSION_LEVEL 1

void compress(z_stream &strm, bool eof) {
    int ret;
    do {
        strm.avail_out = bufsize;
        strm.next_out = out;
        measure_start();
        ret = deflate(&strm, eof ? Z_FINISH : Z_NO_FLUSH);
        measure_end();
        assert(ret==Z_OK || ret==Z_STREAM_END);

        std::cout.write((char*)out, bufsize - strm.avail_out);
    } while(strm.avail_out==0);
}

int main() {

    int ret;
    z_stream strm = {0};
    strm.zalloc = Z_NULL;
    strm.zfree = Z_NULL;
    strm.opaque = Z_NULL;
    strm.next_in = buf;
    strm.avail_in = 0;

    ret = deflateInit2(&strm, COMPRESSION_LEVEL, Z_DEFLATED, windowBits | USE_GZIP, DEFAULT_MEMLEVEL, Z_DEFAULT_STRATEGY);
    assert(ret == Z_OK);


    size_t totalbytes=0;
    
    while(true) {
        std::cin.read((char*)buf, bufsize);
        size_t bytes = std::cin.gcount();
        if(bytes <= 0)
            break;
        totalbytes += bytes;

        strm.avail_in = bytes;
        strm.next_in = buf;

        compress(strm, false);
    }

    compress(strm, true);
    deflateEnd(&strm);
    measure_write("gzip", "cpu", totalbytes);

    return 0;
}
