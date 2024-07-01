#include <iostream>
#include <zlib.h>
#include "util.h"

#define windowBits 15
#define USE_GZIP 16
#define DEFAULT_MEMLEVEL 8
#define COMPRESSION_LEVEL 1

void func(std::string_view &input, std::stringstream &output)
{
    const char *buf = input.data();
    size_t bytes = input.size();

    int ret;
    z_stream strm = {0};
    strm.zalloc = Z_NULL;
    strm.zfree = Z_NULL;
    strm.opaque = Z_NULL;
    strm.next_in = (unsigned char*)buf; //is this ok?
    strm.avail_in = 0;

    ret = deflateInit2(&strm, COMPRESSION_LEVEL, Z_DEFLATED, windowBits | USE_GZIP, DEFAULT_MEMLEVEL, Z_DEFAULT_STRATEGY);
    assert(ret == Z_OK);

    strm.avail_in = bytes;
    strm.next_in = (unsigned char*)buf; //is this ok?

    do {
        const int bufsize = 1024*1024;
        unsigned char out[bufsize];

        strm.avail_out = bufsize;
        strm.next_out = out;
        ret = deflate(&strm, Z_FINISH);
        assert(ret==Z_OK || ret==Z_STREAM_END);

        output.write((char*)out, bufsize - strm.avail_out);
    } while(strm.avail_out==0);

    deflateEnd(&strm);
}
