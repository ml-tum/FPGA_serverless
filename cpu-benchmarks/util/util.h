#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <sstream>
#include <string>
#include <string_view>


extern void func(std::string_view &input, std::stringstream &output);


struct timespec ts_measure_start, ts_measure_end;
long long int measure_nanos=0;

void measure_start() {
    clock_gettime(CLOCK_REALTIME, &ts_measure_start);
}

void measure_end() {
    clock_gettime(CLOCK_REALTIME, &ts_measure_end);
    measure_nanos += (ts_measure_end.tv_sec-ts_measure_start.tv_sec)*(long long int)1e9 
        + (ts_measure_end.tv_nsec-ts_measure_start.tv_nsec);
}

void measure_write(const char* application, const char* plattform, size_t input_size) {
    assert(strcmp(plattform,"cpu")==0);

    char* homedir = getenv("HOME");
    char path[256];
    snprintf(path, sizeof path, "%s/computation_time/log.csv", homedir);

    if(access(path, F_OK) == 0) {
        FILE *fd;
        fd = fopen(path, "a");
        fprintf(fd, "%s, %s, 0, %ld, %lld\n", application, plattform, input_size, measure_nanos);
        fclose(fd);
    }
}

const int bufsize = 64*1024*1024;
char inbuf[bufsize];

int main() {
    std::cin.read((char*)inbuf, bufsize);
    size_t read = std::cin.gcount();
    assert((std::cin.get(), std::cin.eof()));

    std::string_view input{inbuf, read};
    std::stringstream output;

    measure_start();
    func(input, output);
    measure_end();

    std::cout<<output.str();

    std::cerr<<"\nElapsed time: "<<measure_nanos<<" ns";

    return 0;
}
