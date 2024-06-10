#include <immintrin.h>
#include <vector>
#include <iostream>
#include <cassert>
#include <fftw3.h>
#include "../util/util.h"
#include <complex>
using namespace std;

const int N=32768;
using DT = float;

const int BUFSIZE = 64*1024*1024;
float buf[BUFSIZE];
float outbuf[N];

int main()
{

    std::cin.read((char*)buf, BUFSIZE);
    size_t bytes = std::cin.gcount();
    int frames = bytes/sizeof(DT)/N;

    assert(bytes%(N*sizeof(DT))==0);
    assert(cin.eof());
    
    measure_start();
    fftwf_complex* in = (fftwf_complex*) fftwf_malloc(sizeof(fftwf_complex) * N * frames);
    fftwf_complex* out = (fftwf_complex*) fftwf_malloc(sizeof(fftwf_complex) * N * frames);
    fftwf_plan plan = fftwf_plan_dft_1d(N, in, out, FFTW_FORWARD, FFTW_ESTIMATE);
    measure_end(); 

    for(int i=0; i<frames*N; i++) {
        in[i][0] = buf[i];
        in[i][1] = 0;
    }

    for(int i=0; i<frames; i++) {
        measure_start();
        fftwf_execute_dft(plan, in, out);
        for(int i=0; i<N; i++) {
            in[i][0] = out[i][0]*out[i][0] + out[i][1]*out[i][1];
            in[i][1] = 0;
        }
        fftwf_execute_dft(plan, in, out);
        for(int i=0; i<N; i++) {
            out[i][0] /= N;
        }
        measure_end();

        for(int j=0; j<N; j++) {
            outbuf[j] = out[j][0];
        }

        std::cout.write((char*)outbuf, N*sizeof(DT));
    }

    fftwf_destroy_plan(plan);
    fftwf_free(in);
    fftwf_free(out);

    measure_write("fft", "cpu", bytes);

    return 0;
}
