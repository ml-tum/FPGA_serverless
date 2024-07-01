#include <immintrin.h>
#include <vector>
#include <iostream>
#include <cassert>
#include <fftw3.h>
#include "util.h"
#include <complex>
using namespace std;

const int N=32768;
using DT = float;

float outbuf[N];

void func(std::string_view &input, std::stringstream &output)
{
    const char* buf = input.data();
    size_t bytes = input.size();
    int frames = bytes/sizeof(DT)/N;

    assert(bytes%(N*sizeof(DT))==0);
    
    fftwf_complex* in = (fftwf_complex*) fftwf_malloc(sizeof(fftwf_complex) * N * frames);
    fftwf_complex* out = (fftwf_complex*) fftwf_malloc(sizeof(fftwf_complex) * N * frames);
    fftwf_plan plan = fftwf_plan_dft_1d(N, in, out, FFTW_FORWARD, FFTW_ESTIMATE);
    
    for(int i=0; i<frames*N; i++) {
        in[i][0] = ((float*)buf)[i];
        in[i][1] = 0;
    }

    for(int i=0; i<frames; i++) {
        fftwf_execute_dft(plan, in+i*N, out);
        for(int i=0; i<N; i++) {
            in[i][0] = out[i][0]*out[i][0] + out[i][1]*out[i][1];
            in[i][1] = 0;
        }
        fftwf_execute_dft(plan, in, out);
        for(int i=0; i<N; i++) {
            out[i][0] /= N;
        }

        for(int j=0; j<N; j++) {
            outbuf[j]=out[j][0];
        }

        output.write((char*)outbuf, N*sizeof(DT));
    }

    fftwf_destroy_plan(plan);
    fftwf_free(in);
    fftwf_free(out);
}
